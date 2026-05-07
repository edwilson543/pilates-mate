import fastapi


def not_authorized_error(detail: str) -> fastapi.HTTPException:
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
