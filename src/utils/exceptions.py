from fastapi import HTTPException


class NotiHubBaseError(Exception):
    pass

class ObjectNotFoundError(NotiHubBaseError):
    pass

class UserNotFoundError(ObjectNotFoundError):
    pass

class TemplateNotFoundError(ObjectNotFoundError):
    pass

class TemplateCategoryNotFoundError(ObjectNotFoundError):
    pass

class ObjectExistsError(NotiHubBaseError):
    pass

class UserExistsError(ObjectExistsError):
    pass

class TemplateCategoryExistsError(ObjectExistsError):
    pass

class InvalidDBDataError(NotiHubBaseError):
    pass

class LoginDataError(NotiHubBaseError):
    pass

#########################################

class NotiHubBaseHTTPError(HTTPException):
    status_code = 500
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

class UserNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail="Пользователь не найден"

class TemplateSyntaxHTTPError(NotiHubBaseHTTPError):
    status_code=422
    detail="Синтаксическая ошибка в шаблоне"

class NotAuthenticatedError(NotiHubBaseHTTPError):
    status_code=401
    detail="Пользователь не аутентифицирован"

class LoginDataHTTPError(NotiHubBaseHTTPError):
    status_code=401
    detail="Неверные логин или пароль"

class ObjectExistsHTTPError(NotiHubBaseHTTPError):
    status_code=409
    detail="Объект уже существует"

class UserExistsHTTPError(NotiHubBaseHTTPError):
    status_code=409
    detail="Пользователь с таким логином уже существует"

class TemplateCategoryExistsHTTPError(ObjectExistsHTTPError):
    detail="Категория для шаблона уже существует"

class OnlyStaffHTTPError(NotiHubBaseHTTPError):
    status_code=403
    detail="Доступно только администраторам"
    