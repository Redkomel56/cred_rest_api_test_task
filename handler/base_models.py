from pydantic import BaseModel, Field
from utils.register_modeles import register_schema
from loader import app


class Error(BaseModel):
    success: bool = False
    error: str
    fields: dict[str, str] = None


class Success(BaseModel):
    success: bool = True
    message: str = Field(default=None)
    data: list | dict | object = Field(default=None)


register_schema(app, Error)
register_schema(app, Success)
