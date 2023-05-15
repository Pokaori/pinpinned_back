
from fastapi import FastAPI

from routers import user, auth, event

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(event.router)
