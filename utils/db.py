import os
from dotenv import load_dotenv
from pymongo import MongoClient
from loguru import logger

load_dotenv()

uri = os.getenv("MONGO_URI")
mongo_client = None


def get_db():
    global mongo_client
    if mongo_client is None:
        logger.debug("🍃 connecting to db...")
        mongo_client = MongoClient(
            uri,
        )
        logger.debug("connected to db")
    return mongo_client.ebedmano
