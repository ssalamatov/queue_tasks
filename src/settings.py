import os
import pathlib
import yaml


BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')


def get_config():
    with open(DEFAULT_CONFIG_PATH, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg
