"""
Инструмент для логирования
"""

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

    async def info(self, log: str | Exception):
        """
        Writes an info message into the log file.

        Parameters
        ----------
        log: :class:`str`
            Info message
        """
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = self.generate_uid()
        async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
            await file.write(f"[UID: {uid} ] {date_time} - INFO {log}\n")
        print(log + "\n")
        return uid

    async def warning(self, log: str | Exception):
        """
        Writes a warning message into the log file.

        Parameters
        ----------
        log: :class:`str`
            Warning message
        """
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = self.generate_uid()
        async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
            await file.write(f"[UID: {uid} ] {date_time} - WARNING {log}\n")
        print(log + "\n")
        return uid

    async def error(self, log: str | Exception):
        """
        Writes an error message into the log file.

        Parameters
        ----------
        log: :class:`str`
            Error message
        """
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = self.generate_uid()
        async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
            await file.write(f"[UID: {uid} ] {date_time} - ERROR {log}\n")
        print(log + "\n")
        return uid

    async def critical(self, log: str | Exception):
        """
        Writes a critical error message into the log file.

        Parameters
        ----------
        log: :class:`str`
            Critical error message
        """
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uid = self.generate_uid()
        async with aiopen(file=self.file, mode="a", encoding="utf-8") as file:
            await file.write(f"[UID: {uid} ] {date_time} - CRITICAL ERROR {log}\n")
        print(log + "\n")
        return uid
