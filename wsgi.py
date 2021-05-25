from peewee import IntegrityError, DoesNotExist
from sqlite3 import IntegrityError as sqlIE
from flask import Flask, request, make_response, redirect
import json

from model import ShortUrl
from function import create_short_url, check_url
from logging_settings import logger


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def index(path):
    # вытаскиваем необходимые атрибуты
    method, root_url, args = request.method, request.root_url, dict(request.args)
    if method == "GET":  # проверяем что использовался метод GET
        if len(path) == 5:
            # переадрессация проверяем есть ли в базе данных url соответствующий данному short url,
            try:  # проверяем есть ли переданный short url в базе данных
                url = ShortUrl.select().where(ShortUrl.short_url == path).get()
            except DoesNotExist as err:  # если нету сообщаем об этом пользователю
                logger.error(f'{type(err)} : {err}')
                return make_response("<h1>YOUR SHORT URL NOT IN DATABASE</h1>", 404)
            else:  # если есть переадрессовываем
                logger.info(f"On request with short url {path} found url:"
                            f"{url.url} in  database equal user's short url")
                return redirect(url.url, 302)

        args_url = "?" + "&".join([f"{key}={args[key]}" for key in args])  # часть urls с аргументами
        users_urls = args_url[5:]  # url переданный пользователем
        full_urls = root_url + path + args_url  # полный url

        if path.startswith("api/get_long"):
            # получение полного url по короткому
            if not check_url(args):  # проверяем наличие параметра url в запросе
                return make_response("<h1>Your request have not url in params</h1>", 404)
            try:  # проверяем есть ли переданный short url в базе данных
                long = ShortUrl.select().where(ShortUrl.short_url == users_urls).get()
            except DoesNotExist as err:  # если нету сообщаем об этом пользователю
                logger.error(f'{type(err)} : {err}')
                return make_response("<h1>YOUR SHORT URL NOT IN DATABASE</h1>", 404)
            else:  # если есть высылаем полный url
                logger.info(f"On request with short url {path} found url:"
                            f"{long.url} in  database equal user's short url")
                return make_response(json.dumps({users_urls: long.url}), 200)

        if path.startswith("api/get_short"):
            # получение короткого url по полному
            if not check_url(args):  # проверяем наличие параметра url в запросе
                return make_response("<h1>Your request have not url in params</h1>", 404)
            # проверяем есть ли такой url в базе данных
            try:
                short = ShortUrl.select().where(ShortUrl.url == users_urls).get()
            except DoesNotExist as err:  # если нету
                logger.error(f'{type(err)} : {err}')
                # генерируем short url, делаем запись в базу данных и возвращаем результат
                while True:  # пока не будет сгенерирован уникальный short url
                    short = create_short_url()
                    short_url = ShortUrl(url=users_urls, short_url=short)
                    try:
                        short_url.save()
                    except sqlIE as err:
                        logger.error(f'{type(err)} : {err}')
                    except IntegrityError as err:
                        logger.error(f'{type(err)} : {err}')
                    else:
                        break
                logger.info(f"In database was create new short url: {short} for user's request url: {users_urls}")
                return make_response(json.dumps({users_urls: short}), 200)
            else:
                # если есть то ничего создавать не нужно, возвращаем short url из базы данных
                logger.info(f"On request with url: {users_urls} found short_url:"
                            f"{ short.short_url} in  database equal user's short url")
                return make_response(json.dumps({users_urls: short.short_url}), 200)
    else:  # для всех других методов
        logger.error(f'Invalid request method {method}')
        return make_response("YOU MUST USE GET METHOD", 404)

    logger.error(f'Invalid request {full_urls}')
    return make_response("Invalid request", 404)


if __name__ == "__main__":
    ShortUrl.create_table()
    app.run()
