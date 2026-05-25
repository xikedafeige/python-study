# routers/chat.py
import json

import requests
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from config import API_KEY, BASE_URL
from schemas import ChatRequest

router = APIRouter(prefix="/api/ai", tags=["AI"])


def real_ai_stream_generator(user_msg: str, history: list):
    if not API_KEY:
        yield "AI reply failed: missing QIANWEN_API_KEY in .env."
        return

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        *history,
        {"role": "user", "content": user_msg},
    ]

    response = None
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            },
            json={
                "model": "qwen-turbo",
                "messages": messages,
                "stream": True,
            },
            stream=True,
            timeout=(10, 60),
        )

        if response.status_code != 200:
            yield (
                "AI reply failed: upstream returned "
                f"{response.status_code}, {response.text}"
            )
            return

        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue

            data = line[6:]
            if data == "[DONE]":
                break

            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue

            choices = payload.get("choices") or []
            if not choices:
                continue

            content = choices[0].get("delta", {}).get("content")
            if content:
                yield content
    except requests.Timeout:
        yield "AI reply failed: upstream request timed out."
    except requests.RequestException as exc:
        yield f"AI reply failed: upstream request error: {exc}"
    finally:
        if response is not None:
            response.close()


@router.post("/real_stream")
async def real_ai_chat(req: ChatRequest):
    return StreamingResponse(
        real_ai_stream_generator(req.message, req.history),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
