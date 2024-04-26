from utils.db_connector.base_structures import *
from .models import ArticleShortModel


class Article(AccountPostBaseModel):
    title: str
    text: str

    collection_name: ClassVar[str] = MongoCollectionsEnum.ARTICLES

    @classmethod
    def get(cls, object_id):
        collection = cls._db[cls.collection_name]
        document = collection.find_one({"_id": ObjectId(object_id)})
        if document:
            return cls(**document)
        raise UndefinedDocumentType

    @classmethod
    def create(cls, title: str, text: str) -> object:
        user = cls(
            title=title,
            text=text
        )
        user.save()
        return user

    def get_short_model(self) -> ArticleShortModel:
        return ArticleShortModel(
            id=self.id,
            title=self.title,
            text=self.text,
            status=self.system.status
        )

    # @MongoDBModel.mongo_transaction()
    # Можно использовать транзакции, если база монги поднятя в формате rs0 (нод)
    def update(self, title: str = None, text: str = None):
        if title:
            self.title = title
        if text:
            self.text = text
        self.save()

    @classmethod
    def example(cls):
        return cls(
            _id=ObjectId(),
            title='test',
            text='test',
        )
