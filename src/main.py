import uvicorn

from fastapi import FastAPI
from database import Base, engine

from config import get_settings

from routes import router_users, router_tasks, router_tokens, router_friend

settings = get_settings()

app = FastAPI()

app.include_router(router_users)
app.include_router(router_tasks)
app.include_router(router_tokens)
app.include_router(router_friend)

if __name__ == "__main__":



    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=2)
    Base.metadata.create_all(engine)