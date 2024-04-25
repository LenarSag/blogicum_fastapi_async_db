from fastapi import APIRouter, Response, HTTPException, Depends, status
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import GroupRepository
from db.database import get_session
from db.schemas import GroupCreate, GroupDB, GroupPosts, UserAuth
from security.security import get_user_from_token
from db.models import Group


groupsrouter = APIRouter()


async def is_slug_unique(session: AsyncSession, slug: str):
    result = await GroupRepository.get_group_by_slug(session, slug)
    if result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Slug should be unique"
        )
    return True


async def get_group_or_404(session: AsyncSession, group_id: int) -> Group:
    group = await GroupRepository.get_group(session, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Group not found"
        )
    return group


@groupsrouter.post("/", response_model=GroupDB)
async def create_group(
    group_data: GroupCreate = Depends(),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    await is_slug_unique(session, group_data.slug)
    group = await GroupRepository.create_group(session, group_data)
    return group


@groupsrouter.get("/", response_model=Page[GroupDB])
async def get_groups(session: AsyncSession = Depends(get_session)):
    groups = await GroupRepository.get_groups(session)
    if groups:
        return paginate(groups)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Groups not found"
    )


@groupsrouter.get("/{group_id}/", response_model=GroupPosts)
async def get_group(group_id: int, session: AsyncSession = Depends(get_session)):
    group = get_group_or_404(session, group_id)
    return group


@groupsrouter.put("/{group_id}", response_model=GroupDB)
async def update_group(
    group_id: int,
    new_group_data: GroupCreate = Depends(),
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    group = get_group_or_404(session, group_id)
    await is_slug_unique(session, new_group_data.slug)
    updated_group = await GroupRepository.update_group(session, group, new_group_data)
    return updated_group


@groupsrouter.delete("/{group_id}")
async def delete_group(
    group_id: int,
    session: AsyncSession = Depends(get_session),
    user_auth: UserAuth = Depends(get_user_from_token),
):
    group = get_group_or_404(session, group_id)
    result = await GroupRepository.delete_group(session, group)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


add_pagination(groupsrouter)
