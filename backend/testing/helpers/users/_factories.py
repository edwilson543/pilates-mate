import typing

import factory

from pilates.domain import unit_of_work, users


class User(factory.Factory):
    class Meta:
        model = users.User
        exclude = ("password",)

    id = factory.Sequence(lambda n: n)
    full_name = factory.Sequence(lambda n: f"full-name-{n}")
    email = factory.Sequence(lambda n: f"fake-{n}@gmail.com")
    password = factory.Sequence(lambda n: f"password-{n}")

    @factory.lazy_attribute
    def hashed_password(obj: typing.Self) -> str:
        return users.AuthService.hash_password(password=str(obj.password))

    @classmethod
    def insert(cls, uow: unit_of_work.UnitOfWork, **kwargs: object) -> users.User:
        user = cls.create(**kwargs)
        user_id = uow.users.create_user(
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
        )
        user.id = user_id
        return user
