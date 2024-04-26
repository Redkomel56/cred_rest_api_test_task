from .base_exeptions import *


class InvalidObjectId(CustomError):
    """ObjectId инвалид."""
    def __init__(self, message="Invalid object_id"):
        super().__init__(message)


class RootNotFoundError(CustomError):
    """Родительский элемент не найден."""
    def __init__(self, message="Not find root post", status_code=404):
        super().__init__(message, status_code)


class RootOwnerNotFoundError(CustomError):
    """Создатель родительского элемента не найден"""
    def __init__(self, message="Root owner not found", status_code=400):
        super().__init__(message, status_code)


class CountAPIError(CustomError):
    """Ошибка при установки count для коммента родителя"""
    def __init__(self, message="Error setting comment counter"):
        super().__init__(message)


class InvalidRelationsKeyError(CustomError):
    """Ключ для создания зависимости не поддерживается"""
    def __init__(self, message="Key to create relations not support"):
        super().__init__(message)


class InvalidRelationsNotFoundError(CustomError):
    """Создать счетчик можно только при созданной связи"""
    def __init__(self, message="To create a counter you need an already created relations"):
        super().__init__(message)


class DocumentsNotFoundError(CustomError):
    """Документы не найдены"""
    def __init__(self, message="Documents not found"):
        super().__init__(message)