from fastapi import HTTPException


class NotiHubBaseError(Exception):
    pass

class ObjectNotFoundError(NotiHubBaseError):
    pass

class TemplateNotFoundError(ObjectNotFoundError):
    pass

class ObjectExistsError(NotiHubBaseError):
    pass

class InvalidDBDataError(NotiHubBaseError):
    pass

#########################################

class NotiHubBaseHTTPError(HTTPException):
    pass

class ObjectNotFoundHTTPError(NotiHubBaseHTTPError):
    pass

class TemplateNotFoundHTTPError(ObjectNotFoundHTTPError):
    pass
