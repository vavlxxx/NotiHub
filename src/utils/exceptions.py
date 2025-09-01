from fastapi import HTTPException, status

from src.settings import settings


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


class ChannelValidationError(NotiHubBaseError):
    pass


class ScheduleNotFoundError(ObjectNotFoundError):
    pass


class ScheduleAlreadyExistsError(NotiHubBaseError):
    pass


class ObjectExistsError(NotiHubBaseError):
    pass


class UserExistsError(ObjectExistsError):
    pass


class CategoryExistsError(ObjectExistsError):
    pass


class ChannelExistsError(ObjectExistsError):
    pass


class TemplateExistsError(ObjectExistsError):
    pass


class NotificationExistsError(ObjectExistsError):
    pass


class ValueOutOfRangeError(NotiHubBaseError):
    pass


class LoginDataError(NotiHubBaseError):
    pass


class TokenUpdateError(NotiHubBaseError):
    pass


class TemplateSyntaxCheckError(NotiHubBaseError):
    pass


class MissingTemplateVariablesError(NotiHubBaseError):
    pass


class ChannelInUseError(NotiHubBaseError):
    pass


class CategoryInUseError(NotiHubBaseError):
    pass


class ForbiddenHTMLTemplateError(NotiHubBaseError):
    pass


#########################################


class NotiHubBaseHTTPError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Неизвестная ошибка HTTP"

    def __init__(self, *args, **kwargs):
        exc_detail = self.detail
        if "detail" in kwargs:
            exc_detail = kwargs["detail"]
        super().__init__(status_code=self.status_code, detail=exc_detail)


class WebhookSetupError(NotiHubBaseHTTPError): ...


class ObjectNotFoundHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Объект не найден"


class TemplateNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail = "Шаблон не найден"


class CategoryNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail = "Категория для шаблона не найдена"


class UserNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail = "Пользователь не найден"


class ChannelNotFoundHTTPError(ObjectNotFoundHTTPError):
    detail = "Контактный канал не найден"


class ChannelValidationHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Неверные данные контактного канала"


class NotAuthenticatedError(NotiHubBaseHTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь не аутентифицирован"


class LoginDataHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверные логин или пароль"


class TokenUpdateHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = f"Новый токен доступа можно получать только раз в {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES / 60:.1f} ч., либо выйдя из текущего аккаунта"


class InvalidTokenHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный токен"


class ExpiredTokenHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истёк. Пожалуйста пройдите аутентификацию заново"


class ObjectExistsHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Объект уже существует"


class UserExistsHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с таким логином уже существует"


class ChannelExistsHTTPError(ObjectExistsHTTPError):
    detail = "Такой контактный канал уже существует"


class CategoryExistsHTTPError(ObjectExistsHTTPError):
    detail = "Категория для шаблона уже существует"


class TemplateExistsHTTPError(ObjectExistsHTTPError):
    detail = "Такой шаблон уже существует"


class MissingTemplateVariablesHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class OnlyStaffHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Доступно только для персонала"


class ChannelInUseHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_409_CONFLICT


class TemplateSyntaxCheckHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Неверная синтаксис шаблона"


class NotificationExistsHTTPError(ObjectExistsHTTPError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не удалось создать новые уведомления, так как уже существуют уведомления с такими же параметрами"


class ValueOutOfRangeHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.detail = "Значение выходит за допустимые пределы"


class CategoryInUseHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_409_CONFLICT


class ScheduleNotFoundHTTPError(ObjectNotFoundHTTPError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Расписание не найдено"


class ScheduleAlreadyExistsHTTPError(ObjectExistsHTTPError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Расписание уже существует"


class InvalidDatetimeRangeHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Неверный диапазон даты и времени"


class ForbiddenHTMLTemplateHTTPError(NotiHubBaseHTTPError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Шаблон HTML запрещен"
