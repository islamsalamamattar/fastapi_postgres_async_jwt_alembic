from typing import Annotated, Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import UUID

from app.models.user import User
from app.models.post import Post
from app.models.blog import Blog

from app.schemas.post import Post as PostSchema, PostCreate

from app.core.exceptions import AuthFailedException, BadRequestException, ForbiddenException, NotFoundException
from app.core.database import DBSessionDep
from app.core.jwt import (
    mail_token,
    create_token_pair,
    refresh_token_state,
    decode_access_token,
    add_refresh_token_cookie,
    oauth2_scheme,
    SUB, JTI, EXP,
)

router = APIRouter(
    prefix="/api/post",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

@router.get("/") #, response_model=PostSchema)
async def post_list(
    #token: Annotated[str, Depends(oauth2_scheme)],
    token: str,
    db: DBSessionDep,
):
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_username(db=db, username=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")
    username = user.username
    posts = await Post.find_all_by_username(db=db, username=username)
    return posts

@router.post("/{id}", response_model=PostSchema)
async def post_details(
    token: str,
    db: DBSessionDep,
    id: str = Path(..., title="The ID of the post to delete"),
):
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_username(db=db, username=payload[SUB])
    if not user:
        raise AuthFailedException()
    # Check if the provided ID is a valid UUID
    try:
        uuid_obj = uuid.UUID(id)
    except ValueError:
        raise BadRequestException
    post = await Post.find_by_id(db=db, id=id)
    if post is None:
        raise NotFoundException
    return post

@router.post("/create/", response_model=PostSchema)
async def create_post(
    token: str,
    db: DBSessionDep,
    data: PostCreate
):
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_username(db=db, username=payload[SUB])
    if not user:
        raise AuthFailedException()
    
    # Check if the user is the blog creator
    blog = await Blog.find_by_id(db=db, id=data.blog_id)

    if not blog:
        raise NotFoundException(detail="Blog not found")
    if blog.created_by != user.id:
        raise AuthFailedException(detail="User not blog author")

    # Create the post in the database
    post_data = data.model_dump()
    post_data["blog_id"] = blog.id
    post = Post(**post_data)
    post = await post.create(db=db, **post_data)

    post_schema = PostSchema.model_validate(post.__dict__)
    return post_schema

@router.delete("/delete/{id}", response_model=None)
async def delete_post(
    #token: Annotated[str, Depends(oauth2_scheme)],
    token: str,
    db: DBSessionDep,
    id: str = Path(..., title="The ID of the post to delete"),
):
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_username(db=db, username=payload[SUB])
    if not user:
        raise AuthFailedException()

    # Delete the post by its ID
    deleted_post = await Post.delete(db=db, id=id)
    if not deleted_post:
        raise NotFoundException(detail="Post not found")

    return {"message": "Post deleted successfully"}