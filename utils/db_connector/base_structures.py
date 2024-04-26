import datetime

from pydantic import BaseModel, Field, create_model, NonNegativeInt, model_validator
from bson.objectid import ObjectId
from .base_model import MongoDBModel
from utils.db_connector.base_model import ObjectIdPydanticAnnotation
# from . import articles
from .errors import *
from typing import Annotated, ClassVar, Any, Optional
from enum import Enum


class MongoCollectionsEnum(str, Enum):
    ARTICLES = 'Articles'

    @classmethod
    def contains(cls, value):
        return value in cls._value2member_map_


class StatusEnum(str, Enum):
    VALID = 'valid'
    BLOCKED = "blocked"
    DELETED = 'deleted'

    @classmethod
    def contains(cls, value):
        return value in cls._value2member_map_


class System(BaseModel):
    status: StatusEnum = Field(default=StatusEnum.VALID)
    update_document: datetime.datetime = Field(
        default=datetime.datetime.utcnow())


class AccountPostBaseModel(BaseModel, MongoDBModel):
    system: System = Field(default_factory=System)
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation] = Field(
        default=None, alias='_id')
    _original_data = None

    @property
    def created_at(self):
        if self.id is None:
            raise ValueError('self id is None')
        return int(self.id.generation_time.timestamp())

    def model_post_init(self, __context: Any) -> None:
        self._original_data = self.model_dump(exclude_none=True)
        self._init_mongo()

    def _init_mongo(self):
        self._mongo_model: ClassVar = MongoDBModel()
        self._mongo_model.collection_name = self.collection_name

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj._init_mongo()
        return obj

    @classmethod
    def get(cls, object_id):
        collection = cls._db[cls.collection_name]
        document = collection.find_one({"_id": ObjectId(object_id)})
        if document:
            return cls(**document)
        return None

    def full_delete(self):
        document = self.collection.delete_one({"_id": self.id})
        return None

