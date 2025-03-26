import time

import jwt

from config import JWT_ALGORITHM, JWT_SECRET


async def sign_jwt(username: str) -> str:
    payload = {"username": username, "expires": time.time() + (30 * 24 * 3600)}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decode_jwt(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return None
