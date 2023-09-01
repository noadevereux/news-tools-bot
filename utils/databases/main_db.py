from re import A
from aiosqlite import connect
from typing import Literal
from utils.errors import NotFound


class MainDataBase:
    def __init__(self, filename: str = "main.db") -> None:
        self.file = f"./databases/{filename}"

    async def create_tables(self):
        query = """CREATE TABLE IF NOT EXISTS `makers` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `discord_id` INTEGER CHECK(`discord_id` >= 0) NOT NULL UNIQUE,
            `nickname` VARCHAR(255) NOT NULL UNIQUE,
            `level` INTEGER CHECK(`level` IN (-1, 1, 2, 3, 4)) NOT NULL DEFAULT 1,
            `status` VARCHAR(255) CHECK(`status` IN ('new', 'active', 'inactive')) NOT NULL DEFAULT 'new',
            `warns` INTEGER CHECK(`warns` >= 0) NOT NULL DEFAULT 0,
            `appointment_datetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `account_status` INTEGER CHECK(`account_status` IN (0, 1)) NOT NULL DEFAULT 1
        )"""

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query)
            await connection.commit()

    async def is_maker_exists(self, discord_id: int) -> bool:
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM `makers` WHERE `discord_id` = ?", (discord_id,)
                )
                data = await cursor.fetchall()

        return bool(len(data))

    async def add_maker(
        self,
        discord_id: int,
        nickname: str,
    ) -> bool:
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO `makers` (`discord_id`, `nickname`) VALUES (?, ?)",
                    (discord_id, nickname),
                )
            await connection.commit()

    async def deactivate_maker(self, discord_id: int) -> bool:
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "UPDATE `makers` SET `account_status` = 0 WHERE `discord_id` = ?",
                    (discord_id,),
                )
            await connection.commit()

    async def update_maker(
        self,
        discord_id: int,
        column: Literal[
            "id",
            "discord_id",
            "nickname",
            "level",
            "status",
            "warns",
            "appointment_datetime",
            "account_status",
        ],
        value: str | int,
    ) -> bool:
        query = "UPDATE `makers` SET {} = ? WHERE `discord_id` = ?".format(column)
        parameters = (
            value,
            discord_id,
        )
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, parameters)
            await connection.commit()
        return True

    async def get_all(self) -> list[tuple] | None:
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM `makers`")
                data = await cursor.fetchall()
        return data

    async def get_maker(self, discord_id: int) -> tuple | None:
        """
        Scheme
        ------
        0 - id,
        1 - discord_id,
        2 - nickname,
        3 - level,
        4 - status,
        5 - warns,
        6 - appointment_datetime,
        7 - account_status
        """
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM `makers` WHERE `discord_id` = ?", (discord_id,)
                )
                data = await cursor.fetchone()
        if data:
            return data

    async def get_maker_by_id(self, id: int) -> tuple | None:
        """
        Scheme
        ------
        0 - id,
        1 - discord_id,
        2 - nickname,
        3 - level,
        4 - status,
        5 - warns,
        6 - appointment_datetime,
        7 - account_status
        """
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM `makers` WHERE `id` = ?", (id,))
                data = await cursor.fetchone()
        if data:
            return data

    async def get_publications_by_maker(self, id: int):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM `publications` WHERE `maker_id` = ? AND `status` = 'completed'",
                    (id,),
                )
                data = await cursor.fetchall()

        return data


# await cursor.execute(
#     """CREATE TABLE IF NOT EXISTS `makers` (
#         `id` BIGINT(20) NOT NULL,
#         `nickname` VARCHAR(32) NOT NULL,
#         `level` TINYINT NOT NULL DEFAULT 1,
#         `status` VARCHAR(255) CHECK(`status` IN ('new', 'active', 'inactive')) NOT NULL DEFAULT 'new',
#         `warns` TINYINT NOT NULL DEFAULT 0,
#         `color` VARCHAR(6),
#         `icon_link` VARCHAR(255),
#         `publications` INT UNSIGNED NOT NULL DEFAULT 0,
#         `appointment` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#         `account_status` TINYINT(1) CHECK(`account_status` IN (1, 0)) NOT NULL DEFAULT 1,
#         PRIMARY KEY (`id`)
#     )
#     """
# )


class PublicationsTable(MainDataBase):
    def __init__(self, filename: str = "main.db") -> None:
        super().__init__(filename)

    async def create_tables(self):
        query = """CREATE TABLE IF NOT EXISTS `publications` (
            `id` INTEGER NOT NULL PRIMARY KEY,
            `maker_id` INTEGER,
            `date` DATE NOT NULL,
            `information_creator` INTEGER,
            `status` VARCHAR(255) CHECK(`status` IN ('in_process', 'completed', 'failed')) DEFAULT 'in_process',
            `amount_dp` INTEGER NOT NULL DEFAULT 100,
            `dp_paid_by` INTEGER,
            FOREIGN KEY (`maker_id`) REFERENCES `makers`(`id`),
            FOREIGN KEY (`information_creator`) REFERENCES `makers`(`id`),
            FOREIGN KEY (`dp_paid_by`) REFERENCES `makers`(`id`)
        )"""

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query)

            await connection.commit()

    async def add_publication(self, id: int, date: str, amount_dp: int):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO `publications` (`id`, `date`, `amount_dp`) VALUES (?, ?, ?)",
                    (
                        id,
                        date,
                        amount_dp,
                    ),
                )

            await connection.commit()

    async def update_publication(
        self,
        id: int,
        column: Literal[
            "id",
            "maker_id",
            "date",
            "information_creator",
            "status",
            "amount_dp",
            "dp_paid_by",
        ],
        value: int | str,
    ):
        query = "UPDATE `publications` SET {} = ? WHERE `id` = ?".format(column)

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    query,
                    (
                        value,
                        id,
                    ),
                )

            await connection.commit()

    async def delete_publication(self, id: int):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("DELETE FROM `publications` WHERE `id` = ?", (id,))

            await connection.commit()

    async def is_publication_exists(self, id: int):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM `publications` WHERE `id` = ?", (id,)
                )
                data = await cursor.fetchall()

        return bool(len(data))

    async def get_publication(self, id: int):
        """
        Scheme
        ------
        0 - id

        1 - maker_id

        2 - date

        3 - information_creator

        4 - status

        5 - amount_dp

        6 - dp_paid_by

        """
        is_publication_exists = await self.is_publication_exists(id=id)
        if not is_publication_exists:
            raise NotFound("Publication not found")

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM `publications` WHERE `id` = ?", (id,)
                )
                data = await cursor.fetchone()

        return data

    async def get_all_publications(self):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM `publications`")
                data = await cursor.fetchall()

        return data


class MakerActionsTable(MainDataBase):
    def __init__(self, filename: str = "main.db") -> None:
        super().__init__(filename)

    async def create_tables(self):
        query = """CREATE TABLE IF NOT EXISTS `maker_actions` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `maker_id` INTEGER NOT NULL,
            `made_by` INTEGER NOT NULL,
            `action` VARCHAR(255) CHECK(`action` IN (
                'addmaker',
                'deactivate',
                'setnickname',
                'setdiscord',
                'setlevel',
                'setstatus'
            )),
            `meta` VARCHAR(255),
            `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `reason` VARCHAR(255),
            FOREIGN KEY (`maker_id`) REFERENCES `makers`(`id`),
            FOREIGN KEY (`made_by`) REFERENCES `makers`(`id`)
        )"""

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query)

            await connection.commit()

    async def add_maker_action(
        self,
        maker_id: int,
        made_by: int,
        action: Literal[
            "addmaker",
            "deactivate",
            "setnickname",
            "setdiscord",
            "setlevel",
            "setstatus",
        ],
        meta: str,
        reason: str = None,
    ):
        if not reason:
            reason = "NULL"

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO `maker_actions` (`maker_id`, `made_by`, `action`, `meta`, `reason`) VALUES (?, ?, ?, ?, ?)",
                    (
                        maker_id,
                        made_by,
                        action,
                        meta,
                        reason,
                    ),
                )

            await connection.commit()

    async def get_makers_actions(self, maker_id: int):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM `maker_actions` WHERE `maker_id` = ?", (maker_id,)
                )
                data = await cursor.fetchall()

        return data

    async def get_all_maker_actions(self):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM `maker_actions`")
                data = await cursor.fetchall()

        return data


class PubsActionsTable(MainDataBase):
    def __init__(self, filename: str = "main.db") -> None:
        super().__init__(filename)

    async def create_tables(self):
        query = """CREATE TABLE IF NOT EXISTS `publication_actions` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `pub_id` INTEGER NOT NULL,
            `made_by` INTEGER NOT NULL,
            `action` VARCHAR(255) CHECK(`action` IN (
                'createpub',
                'deletepub',
                'setpub_id',
                'setpub_date',
                'setpub_maker',
                'setpub_status',
                'setpub_amount',
                'setpub_infocreator',
                'setpub_salarypayer'
            )),
            `meta` VARCHAR(255),
            `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `reason` VARCHAR(255),
            FOREIGN KEY (`pub_id`) REFERENCES `publications`(`id`),
            FOREIGN KEY (`made_by`) REFERENCES `makers`(`id`)
        )"""

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query)

            await connection.commit()

    async def add_pub_action(
        self,
        pub_id: int,
        made_by: int,
        action: Literal[
            "createpub",
            "deletepub",
            "setpub_id",
            "setpub_date",
            "setpub_maker",
            "setpub_status",
            "setpub_amount",
            "setpub_infocreator",
            "setpub_salarypayer",
        ],
        meta: str,
        reason: str = None,
    ):
        if not reason:
            reason = "NULL"

        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO `maker_actions` (`maker_id`, `made_by`, `action`, `meta`, `reason`) VALUES (?, ?, ?, ?, ?)",
                    (
                        pub_id,
                        made_by,
                        action,
                        meta,
                        reason,
                    ),
                )

            await connection.commit()

    async def get_pubs_actions(self, pub_id: int):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM `publication_actions` WHERE `pub_id` = ?", (pub_id,)
                )
                data = await cursor.fetchall()

        return data

    async def get_all_pub_actions(self):
        async with connect(self.file) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM `publication_actions`")
                data = await cursor.fetchall()

        return data
