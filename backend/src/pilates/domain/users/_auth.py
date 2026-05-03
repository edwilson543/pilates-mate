import abc
import datetime as dt
import functools

import attrs
import jwt
import pwdlib

from . import _models, _repository


class InvalidCredentials(Exception): ...


class InvalidToken(Exception): ...


class TokenExpired(InvalidToken): ...


class AuthService(abc.ABC):
    @abc.abstractmethod
    def get_token_if_password_valid(self, *, email: str, password: str) -> str:
        """
        Verify the credentials and create an auth token for the user.

        :raises InvalidCredentials: If the email and password don't match an account.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_if_token_valid(self, token: str) -> _models.User:
        """
        Verify the given token, authenticating the user it was issued for.
        """
        raise NotImplementedError

    def hash_password(self, password: str) -> str:
        return self._hasher.hash(password=password)

    def _verify_password(self, *, password: str, hashed_password: str) -> bool:
        return self._hasher.verify(password, hash=hashed_password)

    @functools.cached_property
    def _hasher(self) -> pwdlib.PasswordHash:
        return pwdlib.PasswordHash.recommended()


@attrs.frozen
class JWTAuthService(AuthService):
    repo: _repository.Repository

    jwt_expiry_minutes: int
    secret_key: str
    algorithm: str

    def get_token_if_password_valid(self, *, email: str, password: str) -> str:
        try:
            user = self.repo.get_user(email=email)
        except _repository.UserDoesNotExist as exc:
            raise InvalidCredentials from exc

        if not self._verify_password(
            password=password, hashed_password=user.hashed_password
        ):
            raise InvalidCredentials

        expires_at = dt.datetime.now() + dt.timedelta(minutes=self.jwt_expiry_minutes)
        unencoded_jwt = {"sub": email, "exp": expires_at.timestamp()}
        return jwt.encode(unencoded_jwt, key=self.secret_key, algorithm=self.algorithm)

    def get_user_if_token_valid(self, token: str) -> _models.User:
        try:
            decoded_token = jwt.decode(
                token, key=self.secret_key, algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpired from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidToken from exc

        try:
            email = decoded_token["sub"]
        except KeyError as exc:
            raise InvalidToken("Token did not contain `sub` claim.") from exc

        try:
            user = self.repo.get_user(email=email)
        except _repository.UserDoesNotExist as exc:
            raise InvalidToken(
                "Token `sub` claim referenced non-existent user."
            ) from exc

        return user
