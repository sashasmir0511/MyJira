from starlette.config import Config

config = Config(".env")

DATABASE_URL = config(
    "EE_DATABASE_URL",
    cast=str,
    default="postgresql://yourname:yourpassword@db:5432/test",
)
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"
SECRET_KEY = config(
    "EE_SECRET_KEY",
    cast=str,
    default="78c337395cb16606e0a677743b81ebd22ec9764f2b4b4ea73a03382d90be5d6a",
)
DOC_PATH = config("EE_DOC_PATH", cast=str, default="data")
