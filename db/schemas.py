from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserDB(User, UserBase):
    class Config:
        from_attributes = True


class UserPosts(UserDB):
    posts_author: Optional[list["PostDB"]] = None


class UserComments(UserDB):
    comments_author: Optional[list["CommentDB"]] = None


class UserFollowers(UserDB):
    following: Optional[list["UserDB"]] = None


class UserAuth(BaseModel):
    id: int
    username: str


class Group(BaseModel):
    id: int


class GroupCreate(BaseModel):
    title: str
    slug: str
    description: str


class GroupDB(Group, GroupCreate):
    class Config:
        from_attributes = True


class GroupPosts(GroupDB):
    posts_group: Optional[list["Post"]] = None


class Post(BaseModel):
    id: int


class PostCreate(BaseModel):
    text: str
    group_id: Optional[int] = None


class PostDB(Post, PostCreate):
    image: Optional[str] = None
    pub_date: datetime
    author_id: int

    class Config:
        from_attributes = True


class PostComments(PostDB):
    post_comments: Optional[list["CommentDB"]] = None


class Comment(BaseModel):
    id: int


class CommentCreate(BaseModel):
    text: str


class CommentDB(Comment, CommentCreate):
    author_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True
