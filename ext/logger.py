import traceback
from aiofiles import open as aiopen
from datetime import datetime
import string
import random


class Logger:

    def __init__(self, file: str) -> None:
        self.file = f"./logs/{file}"

    @staticmethod
    async def generate_uid() -> str:
        string_length = 48
        error_uid = ''.join(
            random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=string_length))
        return str(error_uid)

    async def info(self, log_message: str | Exception, exc: Exception = None):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = await self.generate_uid()

        if exc:
            traceback_str = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )

            async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
                await file.write(f"[UID: {uid} ] {date_time} - INFO {log_message}\n{traceback_str}\n")
        else:
            async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
                await file.write(f"[UID: {uid} ] {date_time} - INFO {log_message}\n")

        print(f"{log_message}\n")

        return uid

    async def warning(self, log_message: str | Exception, exc: Exception = None):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = await self.generate_uid()

        if exc:
            traceback_str = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )

            async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
                await file.write(f"[UID: {uid} ] {date_time} - WARNING {log_message}\n{traceback_str}\n")
        else:
            async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
                await file.write(f"[UID: {uid} ] {date_time} - WARNING {log_message}\n")

        print(f"{log_message}\n")

        return uid

    async def error(self, log_message: str | Exception, exc: Exception = None):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = await self.generate_uid()

        if exc:
            traceback_str = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )

            async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
                await file.write(f"[UID: {uid} ] {date_time} - ERROR {log_message}\n{traceback_str}\n")
        else:
            async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
                await file.write(f"[UID: {uid} ] {date_time} - ERROR {log_message}\n")

        print(f"{log_message}\n")

        return uid

    async def critical(self, log_message: str | Exception, exc: Exception = None):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = await self.generate_uid()

        if exc:
            traceback_str = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )

            async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
                await file.write(f"[UID: {uid} ] {date_time} - CRITICAL ERROR {log_message}\n{traceback_str}\n")
        else:
            async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
                await file.write(f"[UID: {uid} ] {date_time} - CRITICAL ERROR {log_message}\n")

        print(f"{log_message}\n")

        return uid
