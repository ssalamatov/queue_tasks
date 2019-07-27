from sqlalchemy import create_engine, MetaData

from src.db import task
from src.settings import get_config


dsn = "postgresql://{user}:{password}@{host}:{port}/{database}"


config = get_config()
db = dsn.format(**config['postgres'])
engine = create_engine(db)


def create_tables():
    meta = MetaData()
    meta.create_all(bind=engine, tables=[task])


def drop_tables():
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[task])


if __name__ == '__main__':
    create_tables()
