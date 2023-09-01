from aiosqlite import connect
from json import dumps, loads

from utils.errors import IncorrectCommandName

class AccessDataBase:

    def __init__(self, filename: str = "access.db") -> None:
        self.file = f"./databases/{filename}"
    
    async def create_table(self):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("""CREATE TABLE IF NOT EXISTS `access` (
                    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    `command` INTEGER NOT NULL UNIQUE,
                    `roles` JSON NOT NULL DEFAULT '[]'
                )""")
            
            await connection.commit()
    
    async def is_command_exists(self, command_name: str) -> bool:
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM `access` WHERE `command` = ?", (command_name,))
                data = await cursor.fetchall()
        
        return bool(len(data))
    
    async def add_command(self, command_name: str):
        is_command_exists = await self.is_command_exists(command_name=command_name)
        if is_command_exists:
            return
        
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("INSERT INTO `access` (`command`) VALUES (?)", (command_name,))
            
            await connection.commit()
    
    async def get_access(self, command_name: str) -> list[int]:
        is_command_exists = await self.is_command_exists(command_name=command_name)
        if not is_command_exists:
            return
        
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT `roles` FROM `access` WHERE `command` = ?", (command_name,))
                data = await cursor.fetchone()
        
        if len(data) < 1:
            return
        
        return loads(data[0])
    
    async def set_access(self, command_name: str, *roles):
        is_command_exists = await self.is_command_exists(command_name)
        if not is_command_exists:
            raise IncorrectCommandName
        
        roles_json = dumps(roles)

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("UPDATE `access` SET `roles` = ? WHERE `command` = ?", (roles_json, command_name,))
            
            await connection.commit()
    
    async def get_all(self) -> list[tuple]:
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM `access`")
                data = await cursor.fetchall()
        
        return data