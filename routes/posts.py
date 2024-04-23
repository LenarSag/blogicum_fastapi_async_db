from fastapi import APIRouter, Depends
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from security.security import get_user_from_token
from db.database import get_session
from db.schemas import PostCreate, PostDB, UserAuth
from db.crud import PostRepository


postsrouter = APIRouter()


@postsrouter.get("/", response_model=Page[PostDB])
async def get_posts(
    session: AsyncSession = Depends(get_session),
):
    posts = await PostRepository.get_posts(session)
    return paginate(posts)


@postsrouter.post("/", response_model=PostDB)
async def create_post(
    post_data: PostCreate = Depends(),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    user_id = user_auth.id
    post = await PostRepository.create_post(session, post_data, user_id)
    return post


add_pagination(postsrouter)
