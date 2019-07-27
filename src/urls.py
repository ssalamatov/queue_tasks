import pathlib

from .views import Handler


PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):

    handler = Handler(app, 2)
    app.router.add_post('/task', handler.create_task)
    app.router.add_get(r'/task/{id:\d+}', handler.get_task)
