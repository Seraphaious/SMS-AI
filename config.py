import os
import logging
from dotenv import load_dotenv


load_dotenv()

logging.getLogger("openai").setLevel(logging.WARNING)

PORT = os.getenv("PORT")
BAUD_RATE = int(os.getenv("BAUD_RATE"))

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = os.getenv("PINECONE_REGION")
INDEX = os.getenv("PINECONE_INDEX")
WHITELISTED_NUMBERS = os.environ.get('WHITELISTED_NUMBERS', '').split(',')



