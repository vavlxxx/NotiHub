import re
import logging

from src.utils.db_manager import DB_Manager
from src.utils.enums import ContentType, NotificationStatus
from src.schemas.notifications import AddLogDTO, RequestAddLogDTO
from src.db import sessionmaker_null_pool


logger = logging.getLogger("src.utils.notigfication_helper")


class NotificationHelper:
    def __init__(
        self,
        log_schema: RequestAddLogDTO,
    ):
        self.log_schema = log_schema

    async def _insert_result_into_database(self, data: AddLogDTO):
        async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
            await db.notification_logs.add(data)
            await db.commit()

    async def log_result(
        self,
        status: NotificationStatus = NotificationStatus.FAILURE,
        details: str | None = None,
    ):
        new_log_schema = AddLogDTO(
            **self.log_schema.model_dump(),
            details=details,
            status=status,
        )
        logger.info("New log, after sending notification: %s", new_log_schema)
        await self._insert_result_into_database(new_log_schema)

    @staticmethod
    def detect_content_type(text: str) -> ContentType:
        if not text:
            return ContentType.PLAIN

        html_tags = re.findall(r"<[^>]+>", text)
        if html_tags:
            valid_html_pattern = r"<(?:/?[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?|!--.*?--)>"
            if re.search(valid_html_pattern, text, re.DOTALL | re.IGNORECASE):
                return ContentType.HTML

        return ContentType.PLAIN
