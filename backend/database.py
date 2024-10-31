from sqlmodel import SQLModel, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_test_engine():
    engine = create_engine(
        "sqlite:///test.db", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    return engine
