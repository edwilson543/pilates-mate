import attrs

from pilates.domain import users


@attrs.mutable(kw_only=True)
class FakeRepository(users.Repository):
    _users: list[users.User] = attrs.field(factory=list)

    def create_user(self, *, email: str, hashed_password: str) -> int:
        user = users.User(
            id=self._next_user_id(),
            full_name="Fake",
            email=email,
            hashed_password=hashed_password,
        )
        self._users.append(user)
        return user.id

    def get_user(self, *, email: str) -> users.User:
        for user in self._users:
            if user.email == email:
                return user
        raise users.UserDoesNotExist(email=email)

    def _next_user_id(self) -> int:
        return len(self._users) + 1
