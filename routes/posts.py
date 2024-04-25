from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from config import IMAGE_FOLDER
from security.security import get_user_from_token
from db.database import get_session
from db.schemas import PostComments, PostCreate, PostDB, UserAuth
from db.crud import GroupRepository, PostRepository
from db import models
from routes.comments import commentsrouter


postsrouter = APIRouter()


def user_is_author_or_forbidden(post: models.Post, user_auth: UserAuth):
    if post.author_id != user_auth.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return True


async def get_post_or_404(session: AsyncSession, post_id: int):
    post = await PostRepository.get_post(session, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


async def get_group_or_400(session: AsyncSession, group_id: int):
    group = await GroupRepository.get_group(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Group doesn't exist!"
        )
    return True


@postsrouter.post("/", response_model=PostDB)
async def create_post(
    post_data: PostCreate = Depends(),
    image: UploadFile = File(default=None),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    if post_data.group_id:
        await get_group_or_400(session, post_data.group_id)

    file_path = None
    if image:
        file_path = f"{IMAGE_FOLDER}/{image.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
    post = await PostRepository.create_post(session, post_data, file_path, user_auth.id)
    return post


@postsrouter.get("/", response_model=Page[PostDB])
async def get_posts(
    session: AsyncSession = Depends(get_session),
):
    posts = await PostRepository.get_posts(session)
    if posts:
        return paginate(posts)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found")


@postsrouter.get("/{post_id}/", response_model=PostComments)
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
):
    post = await get_post_or_404(session, post_id)
    return post


@postsrouter.put("/{post_id}/", response_model=PostDB)
async def update_post(
    post_id: int,
    new_post_data: PostCreate = Depends(),
    image: UploadFile = File(default=None),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    post = await get_post_or_404(session, post_id)
    user_is_author_or_forbidden(post, user_auth)
    if new_post_data.group_id:
        await get_group_or_400(session, new_post_data.group_id)

    file_path = None
    if image:
        file_path = f"{IMAGE_FOLDER}/{image.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
    updated_post = await PostRepository.update_post(
        session, post, new_post_data, file_path
    )
    return updated_post


@postsrouter.delete("/{post_id}/")
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    post = await get_post_or_404(session, post_id)
    user_is_author_or_forbidden(post, user_auth)

    result = await PostRepository.delete_post(session, post)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


postsrouter.include_router(commentsrouter, prefix="/{post_id}/comments")
add_pagination(postsrouter)
