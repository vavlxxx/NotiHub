from fastapi import HTTPException


class NotiHubBaseError(Exception):
    detail = "Неизвестная ошибка"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)

class ObjectNotFoundError(NotiHubBaseError):
    pass

class UserNotFoundError(ObjectNotFoundError):
    pass

class TemplateNotFoundError(ObjectNotFoundError):
    pass

class CategoryNotFoundError(ObjectNotFoundError):
    pass

class ChannelNotFoundError(ObjectNotFoundError):
    pass

class NotificationNotFoundError(ObjectNotFoundError):
    pass

class ObjectExistsError(NotiHubBaseError):
    pass

class UserExistsError(ObjectExistsError):
    pass

class CategoryExistsError(ObjectExistsError):
    pass

class ChannelExistsError(ObjectExistsError):
    pass

class NotificationExistsError(ObjectExistsError):
    pass

class InvalidDBDataError(NotiHubBaseError):
    pass

class LoginDataError(NotiHubBaseError):
    pass

class TemplateSyntaxCheckError(NotiHubBaseError):
    pass

class MissingTemplateVariablesError(NotiHubBaseError):
    pass

class ChannelInUseError(NotiHubBaseError):
    pass

#########################################

class NotiHubBaseHTTPError(HTTPException):
    status_code = 500
    detail = "Неизвестная ошибка HTTP"

    def __init__(self, *args, **kwargs):
        exc_detail = self.detail
        if "detail" in kwargs:
            exc_detail = kwargs["detail"]
        super().__init__(status_code=self.status_code, detail=exc_detail)

class ObjectNotFoundHTTPError(NotiHubBaseHTTPError):
    status_code=404
    detail="Объект не найден"

class TemplateNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail="Шаблон не найден"

class CategoryNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail="Категория для шаблона не найдена"

class UserNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail="Пользователь не найден"

class ChannelNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail="Контактный канал не найден"

class NotificationNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail="Уведомление не найдено"

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

class ChannelExistsHTTPError(ObjectExistsHTTPError):
    detail="Такой контактный канал уже существует"

class NotificationExistsHTTPError(ObjectExistsHTTPError):
    detail="Такое уведомление у вас уже существует"

class CategoryExistsHTTPError(ObjectExistsHTTPError):
    detail="Категория для шаблона уже существует"

class MissingTemplateVariablesHTTPError(NotiHubBaseHTTPError):
    status_code=422

class OnlyStaffHTTPError(NotiHubBaseHTTPError):
    status_code=403
    detail="Доступно только администраторам"
