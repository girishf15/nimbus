"""
Semantic Text Splitter - splits text based on semantic similarity
Uses embeddings to find natural breakpoints between semantically different sections.
"""

from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import OllamaEmbeddings
import logging

logger = logging.getLogger(__name__)


def split_text_semantically(text: str, ollama_base_url: str = "http://localhost:11434", embedding_model: str = "nomic-embed-text") -> list[str]:
    """
    Split text based on semantic similarity using embeddings.
    
    This splitter uses embeddings to determine where to split the text,
    creating chunks at natural semantic boundaries rather than arbitrary
    character or token counts.
    
    Args:
        text: The text to split
        ollama_base_url: URL of the Ollama server
        embedding_model: Name of the embedding model to use
        
    Returns:
        List of text chunks split at semantic boundaries
    """
    try:
        logger.info(f"Using SemanticChunker with model: {embedding_model}")
        
        # Initialize Ollama embeddings
        embeddings = OllamaEmbeddings(
            base_url=ollama_base_url,
            model=embedding_model
        )
        
        # Create semantic chunker
        # breakpoint_threshold_type can be:
        # - "percentile": split at points where similarity is below Nth percentile
        # - "standard_deviation": split when similarity is more than N std devs below mean
        # - "interquartile": split at outliers based on IQR
        text_splitter = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=90  # Split at bottom 10% of similarities
        )
        
        # Split the text
        chunks = text_splitter.split_text(text)
        
        logger.info(f"SemanticChunker produced {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            logger.debug(f"Chunk {i+1}: {len(chunk)} chars")
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error in semantic splitting: {e}")
        raise
