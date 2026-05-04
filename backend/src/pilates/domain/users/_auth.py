import abc
import datetime as dt
import enum
import typing

import attrs
import jwt
import pwdlib

from pilates.domain import utils

from . import _models, _repository


class InvalidCredentials(Exception): ...


class InvalidToken(Exception): ...


class TokenExpired(InvalidToken): ...


@attrs.frozen
class Tokens:
    access_token: str
    refresh_token: str


class TokenType(enum.Enum):
    """
    Used to distinguish between JWTs issued for different purposes.
    """

    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class AuthService(abc.ABC):
    @abc.abstractmethod
    def issue_access_and_refresh_token_from_credentials(
        self, *, email: str, password: str
    ) -> Tokens:
        """
        Verify the credentials and issue auth tokens for the user.

        :raises InvalidCredentials: If the email and password don't match an account.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def issue_access_token_from_refresh_token(self, *, refresh_token: str) -> str:
        """
        Verify the refresh token and issue an issue a new access token.

        :raises InvalidToken: If the refresh token is not valid.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_if_access_token_is_valid(self, *, token: str) -> _models.User:
        """
        Verify the access token, returning the user it was issued for.
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

    access_token_expiry_minutes: int
    refresh_token_expiry_minutes: int
    secret_key: str
    algorithm: str

    def issue_access_and_refresh_token_from_credentials(
        self, *, email: str, password: str
    ) -> Tokens:
        try:
            user = self.repo.get_user(email=email)
        except _repository.UserDoesNotExist as exc:
            raise InvalidCredentials from exc

        if not self._verify_password(
            password=password, hashed_password=user.hashed_password
        ):
            raise InvalidCredentials

        access_token = self._create_access_token(email=email)
        refresh_token = self._create_refresh_token(email=email)
        return Tokens(access_token=access_token, refresh_token=refresh_token)

    def issue_access_token_from_refresh_token(self, *, refresh_token: str) -> str:
        user = self._get_user_if_token_is_valid(
            token=refresh_token, required_type=TokenType.REFRESH
        )
        return self._create_access_token(email=user.email)

    def get_user_if_access_token_is_valid(self, *, token: str) -> _models.User:
        return self._get_user_if_token_is_valid(token, required_type=TokenType.ACCESS)

    # Helpers.
    def _get_user_if_token_is_valid(
        self, token: str, *, required_type: TokenType
    ) -> _models.User:
        try:
            decoded_token = jwt.decode(
                token, key=self.secret_key, algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpired from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidToken from exc

        try:
            token_type = TokenType(decoded_token["token_type"])
        except (KeyError, ValueError) as exc:
            raise InvalidToken(
                "Token did not contain valid `token_type` claim."
            ) from exc

        if token_type is not required_type:
            raise InvalidToken("Incorrect value given for `token_type` claim.")

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

    def _create_access_token(self, *, email: str) -> str:
        return self._create_token(
            email=email,
            expiry_minutes=self.access_token_expiry_minutes,
            token_type=TokenType.ACCESS,
        )

    def _create_refresh_token(self, *, email: str) -> str:
        return self._create_token(
            email=email,
            expiry_minutes=self.refresh_token_expiry_minutes,
            token_type=TokenType.REFRESH,
        )

    def _create_token(
        self, *, email: str, expiry_minutes: int, token_type: TokenType
    ) -> str:
        expires_at = utils.now() + dt.timedelta(minutes=expiry_minutes)
        payload = {
            "sub": email,
            "exp": expires_at.timestamp(),
            "token_type": token_type.value,
        }
        return jwt.encode(payload, key=self.secret_key, algorithm=self.algorithm)
