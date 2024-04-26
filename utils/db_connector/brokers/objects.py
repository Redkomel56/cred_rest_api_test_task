
from __future__ import annotations
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from utils.db_connector.errors import *
from config import *

from utils.db_connector.articles import Article
from utils.db_connector.base_structures import MongoCollectionsEnum
from ..filter_builder import FilterBuilder


class ObjectBroker:
    _client = MongoClient(MONGO_DB_URI)
    _db = _client[MONGO_DB_NAME]

    def __init__(self, collection_name: MongoCollectionsEnum):
        self.collection_name = collection_name
        self.collection = self._db[collection_name]

    def list_objects(self, filter: dict = dict(), skip: int = 0, limit: int = 0, required_class: any[Article] = None, sort_by: dict=dict(), randomizer=False, randomizer_size=0) -> list[Article] | list:
        """
        Метод отдает массив найденных объектов в бд, при этом раскидывает в нужные нам модели записей.

        :param filter: Фильтр для монги в формате словаря. Для удобного его создание следует использовать FilterBuilder
        :param skip: Какое количество записей будет пропущено
        :param limit: Количество выводимых записей
        :param required_class: Можно задать, какой класс нам не обходим на выходе. По итогу у нас будет массив только с указанными элементами
        :return: Возвращает массив найденных элементов
        """
        if randomizer:
            pipeline = [
                {'$match': filter},
                {'$sample': {'size': randomizer_size}}
            ]
            if sort_by:
                pipeline.insert(1, {'$sort': sort_by})
            documents = self.collection.aggregate(pipeline)
        else:
            documents = self.collection.find(filter=filter, sort=sort_by, limit=limit, skip=skip)
        temp = []
        for document in documents:
            obj = self._create_instance_from_document(document)
            if obj is None:
                raise Exception('Тип объекта не определен')
            if required_class is not None and not isinstance(obj, required_class):
                continue
            temp.append(obj)
        return temp

    def find_object_by_id(self, object_id) -> any[Article]:
        """
        Поиск любого элемента в коллекции по его _id и автоматическое определение его в модель

        :param object_id: ID искомой записи
        :return: Возвращает найденную запись определенную в модель
        """
        try:
            document = self.collection.find_one({"_id": ObjectId(object_id)})
            if document is None:
                raise RootNotFoundError
            return self._create_instance_from_document(document)
        except InvalidId:
            raise InvalidObjectId

    def _create_instance_from_document(self, document) -> any[Article]:
        """
        Этот метод раскидывает полученные записи из монги по своим классам, если ничего не найдено до выведет ошибку

        :param document: документ из монги, то есть словарь

        """
        if self.collection_name == MongoCollectionsEnum.ARTICLES:
            return Article(**document)
        raise UndefinedDocumentType
