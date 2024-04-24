from typing import Optional

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession


from db import models, schemas


class UserRepository:
    @classmethod
    async def get_user(cls, session: AsyncSession, username: str):
        query = select(models.User).filter_by(username=username)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_user_by_email(cls, session: AsyncSession, email: str):
        query = select(models.User).filter_by(email=email)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def create_user(cls, session: AsyncSession, user_data: schemas.UserCreate):
        db_user = models.User(**user_data.model_dump())
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user


#     @classmethod
#     async def create_referral_user(
#         cls,
#         session: AsyncSession,
#         referral_user: models.User,
#         referrer_user: models.User,
#     ):
#         referrer_user.referral.append(referral_user)
#         await session.commit()
#         await session.refresh(referrer_user)
#         return referral_user


class GroupRepository:
    @classmethod
    async def get_group(cls, session: AsyncSession, group_id: int):
        query = select(models.Group).filter_by(id=group_id)
        result = await session.execute(query)
        return result.scalars().first()


class PostRepository:
    @classmethod
    async def create_post(
        cls,
        session: AsyncSession,
        post_data: schemas.PostCreate,
        file_path: Optional[str],
        user_id: int,
    ):
        db_post = models.Post(
            **post_data.model_dump(), author_id=user_id, image=file_path
        )
        session.add(db_post)
        await session.commit()
        await session.refresh(db_post)
        return db_post

    @classmethod
    async def get_posts(cls, session: AsyncSession):
        query = select(models.Post).order_by(models.Post.pub_date)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_post(cls, session: AsyncSession, post_id):
        query = (
            select(models.Post)
            .filter_by(id=post_id)
            .options(joinedload(models.Post.post_comments))
        )
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def update_post(
        cls,
        session: AsyncSession,
        db_post: models.Post,
        new_post_data: schemas.PostCreate,
        new_file_path: Optional[str],
    ):
        db_post.text = new_post_data.text
        db_post.group_id = new_post_data.group_id
        db_post.image = new_file_path
        await session.commit()
        await session.refresh(db_post)
        return db_post

    @classmethod
    async def delete_post(cls, session: AsyncSession, db_post: models.Post):
        await session.delete(db_post)
        await session.commit()
        return True


class CommentRepository:
    @classmethod
    async def create_comment(
        cls,
        session: AsyncSession,
        comment_data: schemas.CommentCreate,
        post_id: int,
        user_id: int,
    ):
        db_comment = models.Comment(
            **comment_data.model_dump(), post_id=post_id, author_id=user_id
        )
        session.add(db_comment)
        await session.commit()
        await session.refresh(db_comment)
        return db_comment

    @classmethod
    async def get_comment(cls, session: AsyncSession, comment_id: int):
        query = select(models.Comment).filter_by(id=comment_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_comments(cls, session: AsyncSession, post_id: int):
        query = select(models.Comment).filter_by(post_id=post_id)
        result = await session.execute(query)
        return result.scalars().all()


# class ReferralCodeRepository:
#     @classmethod
#     async def get_code(cls, session: AsyncSession, referral_code: str):
#         query = select(models.ReferralCode).filter_by(code=referral_code)
#         result = await session.execute(query)
#         return result.scalars().first()

#     @classmethod
#     async def get_code_by_user(cls, session: AsyncSession, user_id: int):
#         query = select(models.ReferralCode).filter_by(user_id=user_id)
#         result = await session.execute(query)
#         return result.scalars().first()

#     @classmethod
#     async def get_code_by_user_email(cls, session: AsyncSession, email: EmailStr):
#         query = select(models.ReferralCode).join(models.User).filter_by(email=email)
#         result = await session.execute(query)
#         return result.scalars().first()

#     @classmethod
#     async def create_code(
#         cls, session: AsyncSession, code_data: schemas.ReferralCodeCreate, user_id: int
#     ):
#         db_code = models.ReferralCode(user_id=user_id, **code_data.model_dump())
#         session.add(db_code)
#         await session.commit()
#         await session.refresh(db_code)
#         return db_code

#     @classmethod
#     async def update_code(
#         cls,
#         session: AsyncSession,
#         db_code: models.ReferralCode,
#         new_code_data: schemas.ReferralCodeCreate,
#     ):
#         db_code.code = new_code_data.code
#         db_code.description = new_code_data.description
#         db_code.is_active = new_code_data.is_active
#         db_code.expires_at = new_code_data.expires_at
#         await session.commit()
#         await session.refresh(db_code)
#         return db_code

#     @classmethod
#     async def delete_code(cls, session: AsyncSession, db_code: models.ReferralCode):
#         await session.delete(db_code)
#         await session.commit()
#         return True
