from flask_restful import Resource
from flasgger import swag_from
from flask import request, Response
from loader import *
from .models import ArticleUpdateRequest, ArticleGetResponse
from utils.validator import DataValidator
from utils.db_connector import Article, MongoCollectionsEnum, ObjectBroker, FilterBuilder, StatusEnum
from utils.db_connector.errors import CustomError, DocumentsNotFoundError
from handler.base_models import Error, Success
import csv
from io import StringIO


class ArticleMethod(Resource):
    @swag_from({
        'tags': ['Article'],
        'summary': 'Получить статью по ее object_id',
        'parameters': [
            {
                'in': 'path',
                'name': 'article_id',
                'type': 'string',
                'required': True,
                'description': 'object_id статьи'
            }
        ],
        'responses': {
            '200': {
                'description': 'Action executed successfully',
                "schema": {
                    "$ref": '#/definitions/ArticleGetResponse'
                },
            },
            '500': {
                'description': 'Error',
            }
        }
    })
    def get(self, article_id):
        try:
            article = Article.get(article_id)
        except CustomError as e:
            return Error(error=str(e)).model_dump(exclude_none=True), e.status_code

        return DataValidator.object_ids_to_string(ArticleGetResponse(data=article.get_short_model()).model_dump(exclude_none=True, by_alias=True)), 200

    @swag_from({
        'tags': ['Article'],
        'summary': 'Обновить статью по ее object_id',
        'parameters': [
            {
                'in': 'path',
                'name': 'article_id',
                'type': 'string',
                'required': True,
                'description': 'object_id статьи'
            }
        ],
        'responses': {
            '200': {
                'description': 'Action executed successfully',
                "schema": {
                    "$ref": '#/definitions/ArticleGetResponse'
                },
            },
            '400': {
                'description': 'Action executed error',
                'schema': {
                    "$ref": "#/definitions/Error"
                },
            },
            '500': {
                'description': 'Error',
            }
        }
    })
    def put(self, article_id):
        request_data: ArticleUpdateRequest | Error = DataValidator.validate(request.get_json(), ArticleUpdateRequest)
        if isinstance(request_data, Error):
            return request_data.model_dump(), 400
        try:
            article = Article.get(article_id)
            article.update(request_data.title, request_data.text)
        except CustomError as e:
            return Error(error=str(e)).model_dump(exclude_none=True), e.status_code

        return DataValidator.object_ids_to_string(ArticleGetResponse(data=article.get_short_model()).model_dump(exclude_none=True, by_alias=True)), 200

    @swag_from({
        'tags': ['Article'],
        'summary': 'Удалить статью по ее object_id',
        'parameters': [
            {
                'in': 'path',
                'name': 'article_id',
                'type': 'string',
                'required': True,
                'description': 'object_id статьи'
            }
        ],
        'responses': {
            '200': {
                'description': 'Action executed successfully',
                "schema": {
                    "$ref": '#/definitions/Success'
                },
            },
            '500': {
                'description': 'Error',
            }
        }
    })
    def delete(self, article_id):
        try:
            article = Article.get(article_id)
            article.full_delete()
        except CustomError as e:
            return Error(error=str(e)).model_dump(exclude_none=True), e.status_code

        return DataValidator.object_ids_to_string(Success().model_dump(exclude_none=True, by_alias=True)), 200


class ArticleAllMethod(Resource):
    @swag_from({
        'tags': ['Article'],
        'summary': 'Получить все статьи в формате csv',
        'responses': {
            '200': {
                'description': 'Action executed successfully',
            },
            '500': {
                'description': 'Error',
            }
        }
    })
    def get(self):
        try:
            article_example = Article.example()
            filter_engine = FilterBuilder()
            filter_engine.equal(article_example, article_example.system.status, StatusEnum.VALID)
            articles = ObjectBroker(MongoCollectionsEnum.ARTICLES).list_objects(
                filter_engine.build(only_filter=True)
            )
            if len(articles) == 0:
                raise DocumentsNotFoundError()

        except CustomError as e:
            return Error(error=str(e)).model_dump(exclude_none=True), e.status_code
        si = StringIO()
        cw = csv.DictWriter(si, fieldnames=list(article_example.get_short_model().model_dump().keys()))
        cw.writeheader()
        cw.writerows(list(map(lambda article: DataValidator.object_ids_to_string(article.get_short_model().model_dump()), articles)))

        output = si.getvalue()
        return Response(output, mimetype='text/csv', headers={"Content-disposition": "attachment; filename=articles.csv"})


class ArticleCreateMethod(Resource):
    @swag_from({
        'tags': ['Article'],
        'summary': 'Создать статью',
        'responses': {
            '200': {
                'description': 'Action executed successfully',
                "schema": {
                    "$ref": '#/definitions/ArticleGetResponse'
                },
            },
            '400': {
                'description': 'Action executed error',
                'schema': {
                    "$ref": "#/definitions/Error"
                },
            },
            '500': {
                'description': 'Error',
            }
        }
    })
    def post(self):
        request_data: ArticleUpdateRequest | Error = DataValidator.validate(request.get_json(), ArticleUpdateRequest)
        if isinstance(request_data, Error):
            return request_data.model_dump(), 400
        try:
            article = Article.create(request_data.title, request_data.text)
        except CustomError as e:
            return Error(error=str(e)).model_dump(exclude_none=True), e.status_code

        return DataValidator.object_ids_to_string(ArticleGetResponse(data=article.get_short_model()).model_dump(exclude_none=True, by_alias=True)), 200


api.add_resource(ArticleMethod, '/article/<string:article_id>')
api.add_resource(ArticleAllMethod, '/article/getAll')
api.add_resource(ArticleCreateMethod, '/article/create')
