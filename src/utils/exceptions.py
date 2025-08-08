from fastapi import HTTPException


class NotiHubBaseError(Exception):
    pass

class ObjectNotFoundError(NotiHubBaseError):
    pass

class TemplateNotFoundError(ObjectNotFoundError):
    pass

class TemplateCategoryNotFoundError(ObjectNotFoundError):
    pass

class ObjectExistsError(NotiHubBaseError):
    pass

class InvalidDBDataError(NotiHubBaseError):
    pass

#########################################

class NotiHubBaseHTTPError(HTTPException):
    status_code = 400
    detail = "Неизвестная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(status_code=self.status_code, detail=self.detail)

class ObjectNotFoundHTTPError(NotiHubBaseHTTPError):
    status_code=404
    detail="Объект не найден"

class TemplateNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail="Шаблон не найден"

class TemplateCategoryNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail="Категория для шаблона не найдена"

class TemplateSyntaxHTTPError(NotiHubBaseHTTPError):
    status_code=422
    detail="Синтаксическая ошибка в шаблоне"
