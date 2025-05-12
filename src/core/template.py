import os

from fastapi.templating import Jinja2Templates

from database import get_setting


setting = get_setting()

BASE_DIR = setting.BASE_DIR
TEMPLATES_DIR = setting.TEMPLATES_DIR

templates = Jinja2Templates(directory=TEMPLATES_DIR)
