

class DB_Manager:
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    async def __aenter__(self):
        self.session = await self.session_factory()
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
        await self.session.close()
    
    async def check_connection(self):
        await self.session.execute("SELECT 1;")

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()