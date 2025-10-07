"""
Unstructured Parser - Advanced multi-format document parser
Handles PDF, DOCX, HTML, TXT, and many other formats with layout detection.
"""

from pathlib import Path
from unstructured.partition.auto import partition
import logging

logger = logging.getLogger(__name__)


def parse_document_unstructured(file_path: str | Path) -> str:
    """
    Parse a document using the unstructured library.
    
    Supports multiple formats:
    - PDF (with advanced layout detection)
    - DOCX
    - HTML
    - TXT
    - PPTX
    - And many more formats
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Extracted text content
    """
    try:
        file_path = Path(file_path)
        logger.info(f"Parsing {file_path.name} with unstructured library")
        
        # Use partition() which automatically detects the file type
        # and applies the appropriate parser
        elements = partition(
            filename=str(file_path),
            # Strategy options:
            # - "auto": automatically choose best strategy
            # - "fast": faster but less accurate
            # - "hi_res": slower but more accurate (uses OCR if needed)
            strategy="hi_res",  # Changed to hi_res for better image/table handling
            # Include metadata about each element
            include_metadata=True,
        )
        
        # Extract text from all elements
        text_parts = []
        for element in elements:
            # Get the text content
            text = str(element)
            if text.strip():
                text_parts.append(text)
                
                # Log element type and first 100 chars for debugging
                element_type = type(element).__name__
                logger.debug(f"Element ({element_type}): {text[:100]}")
        
        full_text = "\n\n".join(text_parts)
        
        logger.info(f"Unstructured parser extracted {len(full_text)} characters from {file_path.name}")
        logger.info(f"Found {len(elements)} elements in document")
        
        return full_text
        
    except Exception as e:
        logger.error(f"Error parsing {file_path} with unstructured: {e}")
        raise


def parse_document_unstructured_with_layout(file_path: str | Path) -> dict:
    """
    Parse a document and preserve layout information.
    
    Returns structured data with element types, coordinates, and text.
    Useful for documents where layout matters (forms, tables, etc.)
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Dictionary with parsed elements and metadata
    """
    try:
        file_path = Path(file_path)
        logger.info(f"Parsing {file_path.name} with layout preservation")
        
        elements = partition(
            filename=str(file_path),
            strategy="hi_res",  # Use high-resolution strategy for better layout detection
            include_metadata=True,
            include_page_breaks=True,
        )
        
        # Structure the data
        structured_data = {
            "filename": file_path.name,
            "total_elements": len(elements),
            "elements": []
        }
        
        for element in elements:
            element_info = {
                "type": type(element).__name__,
                "text": str(element),
                "metadata": {}
            }
            
            # Extract metadata if available
            if hasattr(element, 'metadata'):
                metadata = element.metadata
                if hasattr(metadata, 'page_number'):
                    element_info["metadata"]["page"] = metadata.page_number
                if hasattr(metadata, 'coordinates'):
                    element_info["metadata"]["coordinates"] = str(metadata.coordinates)
                if hasattr(metadata, 'filename'):
                    element_info["metadata"]["source"] = metadata.filename
            
            structured_data["elements"].append(element_info)
        
        logger.info(f"Extracted {len(elements)} structured elements")
        
        return structured_data
        
    except Exception as e:
        logger.error(f"Error parsing {file_path} with layout: {e}")
        raise
