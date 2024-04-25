from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession


from db import models, schemas


class UserRepository:
    @classmethod
    async def create_user(cls, session: AsyncSession, user_data: schemas.UserCreate):
        db_user = models.User(**user_data.model_dump())
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    @classmethod
    async def get_user(cls, session: AsyncSession, username: str):
        query = (
            select(models.User)
            .filter_by(username=username)
            .options(joinedload(models.User.following))
        )
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_user_by_email(cls, session: AsyncSession, email: str):
        query = select(models.User).filter_by(email=email)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_user_follows(cls, sesion: AsyncSession, username: str):
        query = (
            select(models.User)
            .filter_by(username=username)
            .options(joinedload(models.User.user))
        )
        result = await sesion.execute(query)
        return result.scalars().first()

    @classmethod
    async def follow_user(
        cls, session: AsyncSession, user_to_follow: models.User, follower: models.User
    ):
        user_to_follow.following.append(follower)
        await session.commit()
        await session.refresh(user_to_follow)
        return user_to_follow


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
    async def create_group(cls, session: AsyncSession, group_data: schemas.GroupCreate):
        db_group = models.Group(**group_data.model_dump())
        session.add(db_group)
        await session.commit()
        await session.refresh(db_group)
        return db_group

    @classmethod
    async def get_groups(cls, session: AsyncSession):
        query = select(models.Group).order_by(models.Group.slug)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_group(cls, session: AsyncSession, group_id: int):
        query = (
            select(models.Group)
            .filter_by(id=group_id)
            .options(joinedload(models.Group.posts_group))
        )
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_group_by_slug(cls, session: AsyncSession, slug: str):
        query = select(models.Group).filter_by(slug=slug)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def update_group(
        cls,
        session: AsyncSession,
        db_group: models.Group,
        new_group_data: schemas.GroupCreate,
    ):
        db_group.title = new_group_data.title
        db_group.slug = new_group_data.slug
        db_group.description = new_group_data.description
        await session.commit()
        await session.refresh(db_group)
        return db_group

    @classmethod
    async def delete_group(cls, session: AsyncSession, db_group: models.Group):
        await session.delete(db_group)
        await session.commit()
        return True


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

    @classmethod
    async def update_commnet(
        cls,
        session: AsyncSession,
        db_comment: models.Comment,
        new_comment_data: schemas.CommentCreate,
    ):
        db_comment.text = new_comment_data.text
        await session.commit()
        await session.refresh(db_comment)
        return db_comment

    @classmethod
    async def delete_comment(cls, session: AsyncSession, db_comment: models.Comment):
        await session.delete(db_comment)
        await session.commit()
        return True
