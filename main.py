import os

from fastapi import FastAPI

from routers import user, auth, event, tags, subscription, schedule, comment
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

FRONT_URL = os.getenv("FRONT_URL")
origins = [
    FRONT_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(event.router)
app.include_router(tags.router)
app.include_router(subscription.router)
app.include_router(schedule.router)
app.include_router(comment.router)
