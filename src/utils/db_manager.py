from sqlalchemy import text
from src.repos.templates import (
    TemplateRepository,
    TemplateCategoryRepository
)
from src.repos.users import (
    UserRepository
)


class DB_Manager:
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    async def __aenter__(self):
        self.session = self.session_factory()
        self.templates = TemplateRepository(self.session)
        self.template_categories = TemplateCategoryRepository(self.session)
        self.users = UserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
        await self.session.close()
    
    async def check_connection(self):
        await self.session.execute(text("SELECT 1;"))

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
