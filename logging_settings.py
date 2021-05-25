from loguru import logger


logger.add('log/short_url.log', format='{time} {level} {message}', level='DEBUG')
