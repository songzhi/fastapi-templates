from datetime import timezone, timedelta
import os
from pathlib import Path
import sys

BASE_DIR = Path(os.path.dirname(__file__) if not getattr(
    sys, 'frozen', False) else os.path.dirname(sys.executable))


TZ = timezone(timedelta(hours=8))

IS_TEST: bool = os.environ.get('TEST', False) is not None
IS_DEV: bool = os.environ.get('DEV', False) is not None

AES_KEY = 'lqnqp20serj)4fht'
SECRET_KEY = "09d25e094faa6ca2226c818166b7a2363b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

DATABASE_URL = 'mongodb://localhost:12138'
