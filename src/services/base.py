from src.utils.db_manager import DB_Manager


class BaseService:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager
