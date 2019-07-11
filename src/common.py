import os


def make_database_uri():
    host = os.environ["POSTGRES_HOST"]
    database = os.environ["POSTGRES_DATABASE"]
    port = os.environ["POSTGRES_PORT"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    uri = f"postgres://{user}:{password}@{host}:{port}/{database}"
    return uri
