import asyncio

import uvicorn
from fastapi import FastAPI

from db.database import init_models
from routes.login import loginroute
from routes.posts import postsrouter
from routes.groups import groupsrouter
from routes.follow import followrouter

app = FastAPI()


app.include_router(loginroute, prefix="/auth")
app.include_router(postsrouter, prefix="/posts")
app.include_router(groupsrouter, prefix="/groups")
app.include_router(followrouter, prefix="/follow")


@app.get("/")
async def index():
    return "Blogicum Fastapi"


if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
