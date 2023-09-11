import os

def get_connect_url_train_service():
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME_train_service"]
    if "INSTANCE_UNIX_SOCKET" in os.environ:
        unix_socket_path = os.environ["INSTANCE_UNIX_SOCKET"]
        return f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock={unix_socket_path}/.s.PGSQL.5432"
    else:
        db_host = os.environ["DB_HOST"]
        db_port = os.environ["DB_PORT"]
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

def get_connect_url_feature_service():
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME_feature_service"]
    if "INSTANCE_UNIX_SOCKET" in os.environ:
        unix_socket_path = os.environ["INSTANCE_UNIX_SOCKET"]
        return f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock={unix_socket_path}/.s.PGSQL.5432"
    else:
        db_host = os.environ["DB_HOST"]
        db_port = os.environ["DB_PORT"]
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"