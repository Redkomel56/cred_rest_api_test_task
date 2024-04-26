from utils.db_connector.base_structures import *


class ArticleShortModel(BaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    title: str
    text: str
    status: str