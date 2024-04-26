from loader import app
from utils.db_connector import ArticleShortModel
from utils.register_modeles import register_schema

from ..base_models import Success


class ArticleGetResponse(Success):
    data: ArticleShortModel


class ArticleUpdateRequest(Success):
    title: str | None
    text: str | None


register_schema(app, ArticleGetResponse)
register_schema(app, ArticleUpdateRequest)
