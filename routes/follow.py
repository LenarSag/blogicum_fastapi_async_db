from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import UserRepository
from db.database import get_session
from db.schemas import UserDB, UserAuth
from security.security import get_user_from_token


followingrouter = APIRouter()


async def get_following_user(session: AsyncSession, username: str):
    user = await UserRepository.get_user_with_following(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@followingrouter.get("/", response_model=list[UserDB])
async def get_my_follows(
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    user = await UserRepository.get_user_follows(session, user_auth.username)
    if user.user:
        return user.user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="You are not following anyone"
    )


@followingrouter.post("/{username}/", response_model=str)
async def follow_user(
    username: str,
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    user_to_follow = await get_following_user(session, username)
    if user_to_follow.id == user_auth.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You can't follow yourself!"
        )
    follower = await UserRepository.get_user(session, user_auth.username)
    if follower in user_to_follow.following:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already following this user!",
        )

    user_to_follow = await UserRepository.follow_user(session, user_to_follow, follower)
    if user_to_follow:
        return f"You are followng user {user_to_follow.username}"
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@followingrouter.delete("/{username}/")
async def unfollow_user(
    username: str,
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    user_to_unfollow = await get_following_user(session, username)
    follower = await UserRepository.get_user(session, user_auth.username)

    result = await UserRepository.unfollow_user(session, user_to_unfollow, follower)
    if result:
        return f"You unfollowed user {username}"
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


followersrouter = APIRouter()


@followersrouter.get("/", response_model=list[UserDB])
async def get_my_followers(
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    user = await UserRepository.get_user_followers(session, user_auth.username)
    if user.following:
        return user.following
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="You don't have any followers"
    )


followrouter = APIRouter()

followrouter.include_router(followingrouter, prefix="/following")
followrouter.include_router(followersrouter, prefix="/followers")
