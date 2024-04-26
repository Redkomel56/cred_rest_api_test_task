
from pydantic import BaseModel, ValidationError, Field
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Annotated, Any, ClassVar
from pymongo import MongoClient
from bson import ObjectId
from config import *
import datetime


class ObjectIdPydanticAnnotation:
    @classmethod
    def validate_object_id(cls, v: Any, handler) -> ObjectId:
        if isinstance(v, ObjectId):
            return v

        s = handler(v)
        if ObjectId.is_valid(s):
            return ObjectId(s)
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, _handler) -> core_schema.CoreSchema:
        assert source_type is ObjectId
        return core_schema.no_info_wrap_validator_function(
            cls.validate_object_id,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


class MongoDBModel:
    _client: ClassVar[MongoClient] = MongoClient(MONGO_DB_URI)
    _db: ClassVar = _client[MONGO_DB_NAME]

    @property
    def collection(self):
        if not hasattr(self, '_collection'):
            self._collection: ClassVar = self._db[self.collection_name]
        return self._collection

    def save(self, remove_none=True):
        if hasattr(self, 'system') and hasattr(self.system, 'update_document'):
            self.system.update_document = datetime.datetime.utcnow()
        with self._client.start_session() as session:
            # with session.start_transaction():
            current_data = self.to_dict(remove_none)
            if current_data.get("id") is not None:
                changes = {k: v for k, v in current_data.items() if self._original_data.get(k) != v}
                if changes:
                    self.collection.update_one({'_id': self.id}, {'$set': changes}, session=session)
                self._original_data = current_data
            else:
                result = self.collection.insert_one(current_data, session=session)
                self.id = result.inserted_id
                self._original_data = current_data

    def to_dict(self, remove_none=True):
        result = {}
        for attribute, value in self.__dict__.items():
            if value is not None and attribute not in ['_client', '_db', '_collection', '_original_data', '_mongo_model']:
                key = attribute
                if attribute[-1] == '_':
                    key = attribute[0:-1]
                elif attribute[0] == '_':
                    key = attribute[0:]
                result[key] = self.serialize(value, remove_none)
        return result

    def serialize(self, value, remove_none=True):
        if isinstance(value, BaseModel):
            return value.model_dump(by_alias=True, exclude_none=remove_none)
        elif isinstance(value, list):
            return [self.serialize(item) for item in value]
        elif isinstance(value, dict):
            return {key: self.serialize(val) for key, val in value.items()}
        else:
            return value

    @classmethod
    def from_dict(cls, data):
        if '_id' in data and not isinstance(data['_id'], ObjectId):
            try:
                data['_id'] = ObjectId(data['_id'])
            except Exception as e:
                raise ValueError(f"Invalid '_id' format: {data['_id']}") from e

        transformed_data = {}
        for key, value in data.items():
            transformed_key = key
            transformed_value = value

            if isinstance(value, dict) and hasattr(cls, '__annotations__') and key in cls.__annotations__:
                annotation = cls.__annotations__[key]
                if issubclass(annotation, BaseModel):
                    try:
                        transformed_value = annotation(**value)
                    except ValidationError as e:
                        raise ValueError(f"Validation error for '{key}': {e}")
            #TODO: Перепроверить, так как if elif могу быть не корректными
            if key == 'from':
                transformed_key = '_from'
            elif key == 'list':
                transformed_key = '_from'
            transformed_data[transformed_key] = transformed_value
        try:
            instance = cls(**transformed_data)
        except ValidationError as e:
            raise ValueError(f"Validation error while creating '{cls.__name__}': {e}")

        return instance

    @staticmethod
    def mongo_transaction():
        def decorator(func):
            def wrapper(*args, **kwargs):
                session = MongoDBModel._client.start_session()
                session.start_transaction()
                try:
                    result = func(*args, **kwargs, session=session)
                    session.commit_transaction()
                    return result
                except Exception as e:
                    print(f"Transaction error: {e}")
                    session.abort_transaction()
                finally:
                    session.end_session()

            return wrapper

        return decorator


if __name__ == '__main__':
    class Model(BaseModel):
        id: Annotated[ObjectId, ObjectIdPydanticAnnotation]


    print(Model(id='64b7abdecf2160b649ab6085'))
    print(Model(id='64b7abdecf2160b649ab6085').model_dump_json())
    print(Model(id=ObjectId()))
    print(Model.model_json_schema())
    print(Model(id='foobar'))  # will error
