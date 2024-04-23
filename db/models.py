from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, Text, String, DateTime, Table, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref


class Base(DeclarativeBase):
    pass


user_follow = Table(
    "user_follow",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "follower_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    posts_author: Mapped[list["Post"]] = relationship(
        "Post", back_populates="post_author", cascade="all, delete-orphan"
    )
    comments_author: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="comment_author", cascade="all, delete-orphan"
    )

    user: Mapped[list["User"]] = relationship(
        secondary=user_follow,
        primaryjoin=id == user_follow.c.follower_id,
        secondaryjoin=id == user_follow.c.user_id,
        backref=backref("follow", cascade="all, delete"),
    )

    following: Mapped[list["User"]] = relationship(
        secondary=user_follow,
        primaryjoin=id == user_follow.c.user_id,
        secondaryjoin=id == user_follow.c.follower_id,
        backref=backref("followers", cascade="all, delete"),
    )


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str] = mapped_column(Text(255))

    posts_group: Mapped[list["Post"]] = relationship(
        "Post", back_populates="post_group"
    )


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    pub_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("group.id", ondelete="SET NULL"),
        nullable=True,
    )

    post_author: Mapped["User"] = relationship("User", back_populates="posts_author")
    post_group: Mapped["Group"] = relationship("Group", back_populates="posts_group")
    post_comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="comment_post", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    comment_author: Mapped["User"] = relationship(
        "User", back_populates="comments_author"
    )
    comment_post: Mapped["Post"] = relationship("Post", back_populates="post_comments")
