import datetime as dt


def now() -> dt.datetime:
    return dt.datetime.now(tz=timezone())


def today() -> dt.date:
    return now().date()


def timezone() -> dt.timezone:
    return dt.timezone.utc
