from datetime import datetime
from typing import Union

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from db.schemas import UserCreate, UserDB
from db.crud import UserRepository
from db.database import get_session
from security.pwdcrypt import get_password_hash
from security.security import authenticate_user, create_access_token


loginroute = APIRouter()


@loginroute.post("/registration/", response_model=dict[str, Union[UserDB, str]])
async def create_user(
    user_data: UserCreate = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await UserRepository.get_user_by_email(session, user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    user_data.password = get_password_hash(user_data.password)

    user = await UserRepository.create_user(session, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user"
        )
    return {"user": user, "message": "User created successfully"}


@loginroute.post("/registration_by_code/", response_model=dict[str, Union[UserDB, str]])
async def create_user_referral(
    referral_code: str,
    session: AsyncSession = Depends(get_session),
    referral_user_data: UserCreate = Depends(),
):
    referrer_user = await UserRepository.get_user_by_referral_code(
        session, referral_code
    )
    if referrer_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Referral code not found!"
        )
    if (
        referrer_user.referral_code.expires_at < datetime.now()
        or not referrer_user.referral_code.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Referral code has expired!"
        )

    referral_user = await UserRepository.get_user_by_email(
        session, referral_user_data.email
    )
    if referral_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    referral_user_data.password = get_password_hash(referral_user_data.password)
    new_referral_user = await UserRepository.create_user(session, referral_user_data)

    referral_user = await UserRepository.create_referral_user(
        session, new_referral_user, referrer_user
    )
    return {
        "user": referral_user,
        "message": "User created successfully!",
    }


@loginroute.post("/login/")
async def login_for_access_token(
    session: AsyncSession = Depends(get_session),
    user_data: OAuth2PasswordRequestForm = Depends(),
):
    username = user_data.username
    password = user_data.password

    user = await authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "Bearer"}
