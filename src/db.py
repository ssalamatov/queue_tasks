import aiopg.sa
from sqlalchemy import (MetaData, Table, Column,
                        Integer, Time)

meta = MetaData()

task = Table(
    'task', meta,

    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('create_time', Time, nullable=False),
    Column('start_time', Time, nullable=True),
    Column('exec_time', Time, nullable=True),
)


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port']
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def create_task(conn, create_time):
    return await conn.scalar(
        task.insert()
            .values(create_time=create_time))


async def save_start(conn, id, start_time):
    await conn.execute(
        task.update()
            .values(start_time=start_time)
            .where(task.c.id == id))


async def save_finish(conn, id, exec_time):
    await conn.execute(
        task.update()
            .values(exec_time=exec_time)
            .where(task.c.id == id))


async def get_task_by_id(conn, id):
    result = await conn.execute(
        task.select()
            .where(task.c.id == id))
    return await result.first()
