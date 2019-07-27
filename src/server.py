# -*- coding: utf-8 -*-

from aiohttp import web
from src.db import close_pg, init_pg
from src.settings import get_config
from src.urls import setup_routes


async def init_app():

    app = web.Application()

    app['config'] = get_config()
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)

    setup_routes(app)
    return app


def main():
    app = init_app()

    config = get_config()
    web.run_app(app,
                host=config['host'],
                port=config['port'])


if __name__ == '__main__':
    main()
