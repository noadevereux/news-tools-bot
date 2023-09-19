import uvicorn
from fastapi import APIRouter, FastAPI, Request
from disnake.ext import commands
from config import MAKERS_CHAT_ID


class APIService(FastAPI):
    def __init__(self, bot: commands.Bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot


router = APIRouter()


@router.get("/bot-api/send-notify")
async def index(request: Request):
    bot: commands.Bot = request.app.bot
    ch = bot.get_channel(MAKERS_CHAT_ID)
    await ch.send("Success")
    return {"channel": ch.name}


def make_app(bot):
    app = APIService(bot)
    app.include_router(router)
    return app


async def start_server(bot: commands.Bot) -> None:
    app = make_app(bot)

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8080,  # or whatever
        lifespan="on",
    )

    server = uvicorn.Server(config)
    bot.loop.create_task(server.serve())
