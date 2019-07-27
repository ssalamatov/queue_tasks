
import asyncio
import sys
import subprocess
import functools
import logging
from aiohttp import web
from asyncio import Queue
from .helpers import now, time_to_string

from . import db


run = 'Run'
in_queue = 'In Queue'
completed = 'Completed'

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


async def run_task():
    def _run_task():
        subprocess.Popen('%s %s' % (sys.executable, 'test.py'),
                         shell=True).wait()
    await asyncio.get_event_loop().run_in_executor(None, functools.partial(_run_task))


class Handler:

    def __init__(self, app, limit):
        self.limit = limit
        self.queue = Queue()
        self.event = asyncio.Event()
        self.states = dict()
        self.app = app

        asyncio.ensure_future(self.go())

    async def go(self):
        while True:
            await self.event.wait()
            workers = [asyncio.Task(self.work()) for _ in range(self.limit)]
            await self.queue.join()

            for worker in workers:
                worker.cancel()
            self.event.clear()

    async def work(self):
        try:
            while True:
                id = await self.queue.get()
                self.states[id] = run
                async with self.app['db'].acquire() as conn:
                    await db.save_start(conn, id, now())
                    await run_task()

                    logging.info('%s: done' % id)
                    self.states[id] = completed
                    await db.save_finish(conn, id, now())
                self.queue.task_done()
        except asyncio.CancelledError:
            pass

    async def create_task(self, request):
        if request.method == 'POST':
            async with self.app['db'].acquire() as conn:
                id = await db.create_task(conn, now())
                self.queue.put_nowait(id)
                logging.info('%s: in_queue' % id)
                self.states[id] = in_queue
                self.event.set()
                return web.json_response({'id': id})

        return {}

    async def get_task(self, request):
        id = int(request.match_info['id'])

        if id in self.states:
            state = self.states[id]

            async with request.app['db'].acquire() as conn:
                try:
                    task = await db.get_task_by_id(conn, id)
                    payload = {'id': task.id, 'status': state, 'create_time': time_to_string(task.create_time),
                                              'start_time': time_to_string(task.start_time),
                                              'time_to_execute': time_to_string(task.exec_time)}
                    return web.json_response(payload)

                except:
                    raise web.HTTPNotFound()
        else:
            return web.HTTPBadRequest()
