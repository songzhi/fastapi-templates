from datetime import timezone, timedelta

TZ = timezone(timedelta(hours=8))

AES_KEY = 'lqnqp20serj)4fht'
SECRET_KEY = "09d25e094faa6ca2226c818166b7a2363b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

DATABASE_URL = 'mongodb://localhost:12138'
