from string import ascii_letters, digits
from random import SystemRandom
from logging_settings import logger
from flask import make_response


def create_short_url(n=5) -> str:
    return ''.join([SystemRandom().choice(ascii_letters + digits) for _ in range(n)])


def check_url(args):
    if "url" not in args:  # проверяем наличие параметра url в запросе
        logger.error(f'Request have not url in params: {args}')
        return False
    return True
