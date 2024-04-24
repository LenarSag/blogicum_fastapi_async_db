from fastapi import APIRouter, Depends, Path
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from security.security import get_user_from_token
from db.database import get_session
from db.schemas import CommentCreate, CommentDB, UserAuth
from db.crud import CommentRepository

commentsrouter = APIRouter()


@commentsrouter.post("/", response_model=CommentDB)
async def create_comment(
    comment_data: CommentCreate,
    post_id: int = Path(..., title="The id of the post"),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    user_id = user_auth.id
    comment = await CommentRepository.create_comment(
        session, comment_data, post_id, user_id
    )
    return comment


@commentsrouter.get("/", response_model=Page[CommentDB])
async def get_comments(
    post_id: int = Path(..., title="The id of the post"),
    session: AsyncSession = Depends(get_session),
):
    # post = get_post_or_404(post_id)
    comments = await CommentRepository.get_comments(session, post_id)
    return paginate(comments)


@commentsrouter.get("/{comment_id}", response_model=CommentDB)
async def get_comment(
    comment_id: int,
    post_id: int = Path(..., title="The id of the post"),
    session: AsyncSession = Depends(get_session),
):
    # post = get_post_or_404(post_id)
    comment = await CommentRepository.get_comment(session, comment_id)
    return comment


add_pagination(commentsrouter)
