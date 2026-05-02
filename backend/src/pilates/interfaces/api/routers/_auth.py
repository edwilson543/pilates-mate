import datetime as dt
import typing

import fastapi
import jwt
import pwdlib
import pydantic
from fastapi import security


oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="auth/token")
password_hash = pwdlib.PasswordHash.recommended()
SECRET_KEY = "secret-key-boom"
ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 30

router = fastapi.APIRouter()


class User(pydantic.BaseModel):
    id: int
    email: str
    full_name: str
    hashed_password: str

    @property
    def username(self) -> str:
        return self.email


USERS = {
    "ed@gmail.com": User(
        id=1,
        email="ed@gmail.com",
        full_name="Ed",
        # qwerty123
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$jaYxajn3IfTPUnQhASV2qQ$RhSN+TWkvLb+uz7ZA7oohAY5LAHm6hc3w13eFtfcKq4",
    ),
    "libby@gmail.com": User(
        id=2,
        email="libby@gmail.com",
        full_name="Libby",
        # qwerty1234
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$C1l3xwrnjUp+E1HDrskRPQ$U6UbaFC7HhAqdN+0zTwBsMVRk7x7NcfIX4Fe2pChc2c",
    ),
}


# Auth layer.


def get_user(username: str) -> User:
    return USERS[username]


def create_jwt(*, username: str) -> str:
    expires_at = dt.datetime.now() + dt.timedelta(minutes=JWT_EXPIRY_MINUTES)
    unencoded_jwt = {"sub": username, "exp": expires_at.timestamp()}
    return jwt.encode(unencoded_jwt, key=SECRET_KEY, algorithm=ALGORITHM)


class InvalidToken(Exception):
    pass


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def is_password_correct(*, password: str, hashed_password) -> bool:
    return password_hash.verify(password, hashed_password)


# Deps.


async def get_current_user(
    token: typing.Annotated[str, fastapi.Depends(oauth2_scheme)],
) -> User:
    try:
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.exceptions.ExpiredSignatureError as exc:
        raise _not_authorized_error("Token expired.") from exc
    except jwt.exceptions.InvalidTokenError as exc:
        raise _not_authorized_error("Invalid token.") from exc

    username = decoded_token["sub"]
    return USERS[username]


# Interfaces.
# Auth.


def _not_authorized_error(detail: str) -> fastapi.HTTPException:
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


class TokenResponse(pydantic.BaseModel):
    access_token: str
    token_type: str


@router.post("/token")
async def login(
    form_data: typing.Annotated[security.OAuth2PasswordRequestForm, fastapi.Depends()],
) -> TokenResponse:
    try:
        candidate_user = USERS[form_data.username]
    except KeyError as exc:
        raise _not_authorized_error("Invalid username or password.") from exc

    if not is_password_correct(
        password=form_data.password, hashed_password=candidate_user.hashed_password
    ):
        raise _not_authorized_error("Invalid username or password.")

    token = create_jwt(username=candidate_user.username)
    return TokenResponse(access_token=token, token_type="bearer")


# Items.


class Item(pydantic.BaseModel):
    user_id: int
    details: str


ITEMS_DB = [
    Item(user_id=1, details="ed's item"),
    Item(user_id=2, details="libby's item"),
    Item(user_id=3, details="someone else's item"),
]


@router.get("/items")
async def read_items(
    user: typing.Annotated[User, fastapi.Depends(get_current_user)],
) -> list[Item]:
    return [item for item in ITEMS_DB if item.user_id == user.id]
