from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Downloading BAAI/bge-m3...")
model = SentenceTransformer("BAAI/bge-m3")
logger.info("Download complete.")
