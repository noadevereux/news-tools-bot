from asyncio.exceptions import CancelledError
from fastapi.concurrency import asynccontextmanager
import uvicorn
from fastapi import APIRouter, FastAPI, Request, Depends
from api.auth.auth_bearer import JWTBearer
import disnake
from disnake.ext import commands
from config import MAKERS_CHAT_ID


class APIService(FastAPI):
    def __init__(self, bot: commands.Bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot


router = APIRouter()


@asynccontextmanager
async def lifespan(app: APIService):
    yield
    try:
        await app.bot.close()
    except CancelledError:
        pass
    app.bot.loop.stop()


@router.post("/send_notify", dependencies=[Depends(JWTBearer())], tags=["Notifies"])
async def send_notify(request: Request, message: str):
    bot: commands.Bot = request.app.bot
    channel = bot.get_channel(MAKERS_CHAT_ID)

    try:
        await channel.send(content=message)
    except Exception as error:
        return {"status": "error", "code": "exception", "message": str(error)}

    return {"status": "ok", "message": message}


@router.post("/send_dm_notify", dependencies=[Depends(JWTBearer())], tags=["Notifies"])
async def send_dm_notify(request: Request, user_id: int, message: str):
    bot: commands.Bot = request.app.bot
    user: disnake.User = bot.get_user(user_id)

    if not user:
        return {"status": "error", "code": "not_found", "message": "User not found"}

    try:
        await user.send(content=message)
    except disnake.Forbidden:
        return {
            "status": "error",
            "code": "forbidden",
            "message": "Bot doesn't have permission to message this user",
        }
    except Exception as error:
        return {"status": "error", "code": "exception", "message": str(error)}

    return {"status": "ok", "user": user_id, "message": message}


def make_app(bot):
    app = APIService(bot, lifespan=lifespan)
    app.include_router(router)
    return app


async def start_server(bot: commands.Bot) -> None:
    app = make_app(bot)

    config = uvicorn.Config(
        app, host="0.0.0.0", port=8080, lifespan="on", reload=True, reload_delay=1.0
    )

    server = uvicorn.Server(config)
    bot.loop.create_task(server.serve())
