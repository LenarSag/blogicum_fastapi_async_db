from fastapi import APIRouter, HTTPException, Response, Depends, Path, status
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from security.security import get_user_from_token
from db.database import get_session
from db.schemas import CommentCreate, CommentDB, UserAuth
from db.crud import CommentRepository, PostRepository
from db import models


commentsrouter = APIRouter()


def user_is_author_or_forbidden(comment: models.Comment, user_auth: UserAuth):
    if comment.author_id != user_auth.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return True


async def get_post_or_404(session: AsyncSession, post_id: int):
    post = await PostRepository.get_post(session, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


async def get_comment_or_404(session: AsyncSession, comment_id: int):
    comment = await CommentRepository.get_comment(session, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return comment


@commentsrouter.post("/", response_model=CommentDB)
async def create_comment(
    comment_data: CommentCreate = Depends(),
    post_id: int = Path(..., title="The id of the post"),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    post = await get_post_or_404(session, post_id)
    comment = await CommentRepository.create_comment(
        session, comment_data, post.id, user_auth.id
    )
    return comment


@commentsrouter.get("/", response_model=Page[CommentDB])
async def get_comments(
    post_id: int = Path(..., title="The id of the post"),
    session: AsyncSession = Depends(get_session),
):
    comments = await CommentRepository.get_comments(session, post_id)
    if comments:
        return paginate(comments)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found"
    )


@commentsrouter.get("/{comment_id}", response_model=CommentDB)
async def get_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
):
    comment = await get_comment_or_404(session, comment_id)
    return comment


@commentsrouter.put("/{comment_id}", response_model=CommentDB)
async def update_comment(
    comment_id: int,
    post_id: int = Path(..., title="The id of the post"),
    new_comment_data: CommentCreate = Depends(),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    await get_post_or_404(session, post_id)
    comment = await get_comment_or_404(session, comment_id)
    user_is_author_or_forbidden(comment, user_auth)
    update_comment = await CommentRepository.update_commnet(
        session, comment, new_comment_data
    )
    return update_comment


@commentsrouter.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    post_id: int = Path(..., title="The id of the post"),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    await get_post_or_404(session, post_id)
    comment = await get_comment_or_404(session, comment_id)
    user_is_author_or_forbidden(comment, user_auth)
    result = await CommentRepository.delete_comment(session, comment)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


add_pagination(commentsrouter)
