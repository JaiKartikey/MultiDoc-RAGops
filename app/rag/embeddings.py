from openai import OpenAI

from app.core.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)

client = OpenAI(
    api_key =settings.gemini_api_key,
    base_url = settings.gemini_api_base_url
)

def create_embedding(text):

    logger.info("Creating Embedding")

    response =client.embeddings.create(
        model = "gemini-embedding-001",
        input = text
    )

    return response.data[0].embedding
