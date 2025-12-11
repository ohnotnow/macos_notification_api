import os
import subprocess

from dotenv import load_dotenv
from fastapi import FastAPI, Query, status
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="macOS Notification API")

DEFAULT_TITLE = os.getenv("DEFAULT_TITLE", "Notification")
DEFAULT_MESSAGE = os.getenv("DEFAULT_MESSAGE", "Hello!")
DEFAULT_SOUND = os.getenv("DEFAULT_SOUND", "Sosumi")
CUSTOM_SOUND_PATH = os.getenv("CUSTOM_SOUND_PATH")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))


class NotificationRequest(BaseModel):
    title: str = DEFAULT_TITLE
    message: str = DEFAULT_MESSAGE
    sound: str = DEFAULT_SOUND


def send_notification(title: str, message: str, sound: str) -> None:
    """Send a macOS notification using osascript."""
    if CUSTOM_SOUND_PATH:
        # Play custom sound via afplay
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], check=True)
        subprocess.run(["afplay", f"{CUSTOM_SOUND_PATH}/{sound}"], check=True)
    else:
        # Use built-in system sound
        script = f'display notification "{message}" with title "{title}" sound name "{sound}"'
        subprocess.run(["osascript", "-e", script], check=True)


@app.post("/notify", status_code=status.HTTP_204_NO_CONTENT)
def notify_post(request: NotificationRequest):
    """Send a notification via POST request with JSON body."""
    send_notification(request.title, request.message, request.sound)


@app.get("/notify", status_code=status.HTTP_204_NO_CONTENT)
def notify_get(
    title: str = Query(default=DEFAULT_TITLE),
    message: str = Query(default=DEFAULT_MESSAGE),
    sound: str = Query(default=DEFAULT_SOUND),
):
    """Send a notification via GET request with query parameters."""
    send_notification(title, message, sound)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)

