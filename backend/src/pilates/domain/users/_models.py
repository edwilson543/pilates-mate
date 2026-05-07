import pydantic


class User(pydantic.BaseModel):
    id: int
    full_name: str
    email: str
    hashed_password: str
