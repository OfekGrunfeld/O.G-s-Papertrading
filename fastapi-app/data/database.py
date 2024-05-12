from enum import Enum

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from utils.logger_script import logger

# Databae Names
class DatabasesNames(Enum):
    """
    Names of the databases - Hard coded. 
    It makes for the dynamic databases to be a bit missleading, 
    but it's used as a constant class to simplify using functions
    that need the name of the database.
    """
    userbase = "userbase"
    transactions = "transactions"
    portfolios = "portfolios"

    @classmethod
    def __contains__(cls, item):
        return item in (member.value for member in cls)


def create_database_uri(database_name: str) -> str:
    """
    Generates a URI for connecting to an SQLite database based on the provided database name.

    Args:
        database_name (str): The name of the database to connect to.

    Returns:
        str: A string representing the SQLite URI formatted as 'sqlite:///./<database_name>.sqlite'.
             This URI points to an SQLite file located in the same directory as the script.
    """
    prefix = "sqlite:///./"
    suffix = ".sqlite"

    database_uri= f"{prefix}{database_name}{suffix}"

    return database_uri

default_connect_args = {"check_same_thread": False}

# create engine for userbase
db_engine_userbase = create_engine(
    create_database_uri(DatabasesNames.userbase.value), connect_args=default_connect_args
) 
db_sessionmaker_userbase = sessionmaker(autocommit=False, autoflush=False, bind=db_engine_userbase)
db_base_userbase = declarative_base()

# create engine for transactions 
db_engine_transactions = create_engine(
    create_database_uri(DatabasesNames.transactions.value), connect_args=default_connect_args
) 
db_sessionmaker_transactions = sessionmaker(autocommit=False, autoflush=False, bind=db_engine_transactions)
db_metadata_transactions = MetaData()


# create engine for portfolios 
db_engine_portfolios = create_engine(
    create_database_uri(DatabasesNames.portfolios.value), connect_args=default_connect_args
) 
db_sessionmaker_portfolios = sessionmaker(autocommit=False, autoflush=False, bind=db_engine_portfolios)
db_metadata_portfolios = MetaData()

def initialise_all_databases():
    """
    Initializes all necessary databases by setting up tables and reflecting existing schema.

    Raises:
        Exception: Exceptions occuring while initializing.
    """
    try:
        global db_base_userbase, db_engine_userbase, db_metadata_transactions, db_engine_transactions, db_metadata_portfolios, db_engine_portfolios

        db_base_userbase.metadata.create_all(bind=db_engine_userbase)
        db_metadata_transactions.reflect(bind=db_engine_transactions)
        db_metadata_portfolios.reflect(bind=db_engine_portfolios)
    except Exception as error:
        logger.critical(f"Error initialising databases. Error: {error}")
        raise error
