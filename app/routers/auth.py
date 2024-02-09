from typing import Annotated, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Response, Depends, Cookie, BackgroundTasks, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import ValidationError


from app.core.database import DBSessionDep
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.core.jwt import (
    mail_token,
    create_token_pair,
    refresh_token_state,
    decode_access_token,
    add_refresh_token_cookie,
    oauth2_scheme,
    SUB, JTI, EXP,
)

from app.utils.mail import user_mail_event
from app.utils.hash import hash_password, verify_password

from app.models import User, BlackListToken

from app.schemas.user import (
    User as UserSchema,
    UserRegister,
    UserLogin,
    ForgotPasswordSchema,
    PasswordResetSchema,
    PasswordUpdateSchema,
    OldPasswordErrorSchema,
)
from app.schemas.jwt import JwtTokenSchema, SuccessResponseScheme
from app.schemas.mail import MailBodySchema, EmailSchema, MailTaskSchema



router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=UserSchema)
async def register(
    data: UserRegister,
    bg_task: BackgroundTasks,
    db: DBSessionDep,
):    
    # check if email already registered
    user = await User.find_by_email(db=db, email=data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")    
    # check if username taken
    user = await User.find_by_username(db=db, username=data.username)
    if user:
        raise HTTPException(status_code=400, detail="Username is not available, please try a new one.")
    
    # save user to db
    user_data = data.model_dump(exclude={"confirm_password"})
    user = User(**user_data)
    await user.create(db=db, **user_data)

    # send verify email
    user = await User.find_by_username(db=db, username=data.username)
    user_schema = UserSchema.model_validate(user.__dict__)
    verify_token = mail_token(user_schema)

    mail_task_data = MailTaskSchema(
        user=user_schema, body=MailBodySchema(type="verify", token=verify_token)
    )
    bg_task.add_task(user_mail_event, mail_task_data)

    return user_schema

@router.get("/verify", response_model=SuccessResponseScheme)
async def verify(
    token: str,
    db: DBSessionDep
):
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_email(db=db, email=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    await user.patch(db=db, username=user.username, is_disabled = False)
    return {"msg": "Successfully activated"}

@router.post("/login")
async def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: DBSessionDep,
):    
    user = await User.authenticate(
        db=db, username=data.username, password=data.password
    )
    if not user:
        raise BadRequestException(detail="Incorrect email or password")
    if user.is_disabled:
        raise ForbiddenException()

    user = UserSchema.model_validate(user.__dict__)
    token_pair = create_token_pair(user=user)

    add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    return {"token": token_pair.access.token}


@router.post("/refresh")
async def refresh(refresh: Annotated[str | None, Cookie()] = None):
    print(refresh)
    if not refresh:
        raise BadRequestException(detail="refresh token required")
    return refresh_token_state(token=refresh)



@router.post("/logout", response_model=SuccessResponseScheme)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSessionDep,
):
    payload = await decode_access_token(token=token, db=db)
    token_data = {"id":payload[JTI], "expire":datetime.utcfromtimestamp(payload[EXP])}
    black_listed = BlackListToken(id=payload[JTI], expire=datetime.utcfromtimestamp(payload[EXP]))
    await black_listed.create(db=db, **token_data)

    return {"msg": "Succesfully logout"}


@router.post("/forgot-password", response_model=SuccessResponseScheme)
async def forgot_password(
    data: ForgotPasswordSchema,
    bg_task: BackgroundTasks,
    db: DBSessionDep,
):
    user = await User.find_by_email(db=db, email=data.email)
    if not user:
        return {"msg": "Email is not regestered in our database. Please check the email or register for a new account"}
    else:
        user_schema = UserSchema.model_validate(user.__dict__)
        reset_token = mail_token(user_schema)

        mail_task_data = MailTaskSchema(
            user=user_schema,
            body=MailBodySchema(type="password-reset", token=reset_token),
        )
        bg_task.add_task(user_mail_event, mail_task_data)

    return {"msg": "Reset token sent successfully. Please check your email"}


@router.post("/password-reset", response_model=SuccessResponseScheme)
async def password_reset_token(
    token: str,
    data: PasswordResetSchema,
    db: DBSessionDep,
):
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_email(db=db, email=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")
    username = user.username
    hashed_password = hash_password(data.password)
    await user.patch(db=db, username=username, password=hashed_password)

    return {"msg": "Password succesfully updated"}


@router.post("/password-update", response_model=SuccessResponseScheme)
async def password_update(
    token: Annotated[str, Depends(oauth2_scheme)],
    data: PasswordUpdateSchema,
    db: DBSessionDep,
):
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_username(db=db, username=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    # raise Validation error
    if not verify_password(data.old_password, user.password):
        try:
            OldPasswordErrorSchema(old_password=False)
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors)

    hashed_password = hash_password(data.password)
    await user.patch(db=db, username=payload[SUB], password=hashed_password)

    return {"msg": "Successfully updated"}

