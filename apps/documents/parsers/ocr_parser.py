"""
OCR Parser - Extract text from images and image-heavy PDFs
Includes image detection, OCR, and optional AI-based image description
"""

import logging
from pathlib import Path
from typing import List, Dict
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import requests
import json

logger = logging.getLogger(__name__)


def parse_with_ocr(file_path: str | Path) -> str:
    """
    Parse a document using OCR (Optical Character Recognition).
    
    Best for:
    - Scanned PDFs
    - Image-heavy documents
    - Screenshots converted to PDF
    - Documents with poor text extraction
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Extracted text from images using OCR
    """
    try:
        file_path = Path(file_path)
        logger.info(f"Starting OCR parsing for {file_path.name}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.pdf':
            return _parse_pdf_with_ocr(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return _parse_image_with_ocr(file_path)
        else:
            raise ValueError(f"Unsupported file type for OCR: {file_ext}")
            
    except Exception as e:
        logger.error(f"Error during OCR parsing of {file_path}: {e}")
        raise


def _parse_pdf_with_ocr(pdf_path: Path) -> str:
    """
    Convert PDF pages to images and extract text using OCR.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        OCR-extracted text from all pages
    """
    logger.info(f"Converting PDF to images for OCR: {pdf_path.name}")
    
    try:
        # Convert PDF to images (one per page)
        images = convert_from_path(
            str(pdf_path),
            dpi=300,  # Higher DPI = better OCR accuracy
            fmt='jpeg'
        )
        
        logger.info(f"Converted {len(images)} pages to images")
        
        # Extract text from each page
        all_text = []
        for page_num, image in enumerate(images, start=1):
            logger.debug(f"OCR processing page {page_num}/{len(images)}")
            
            # Use Tesseract OCR
            text = pytesseract.image_to_string(
                image,
                lang='eng',  # Language: English (can add more: 'eng+ara+fra')
                config='--psm 3'  # Page segmentation mode: 3 = Fully automatic
            )
            
            if text.strip():
                all_text.append(f"=== Page {page_num} ===\n{text.strip()}")
        
        full_text = "\n\n".join(all_text)
        logger.info(f"OCR extracted {len(full_text)} characters from {len(images)} pages")
        
        return full_text
        
    except Exception as e:
        logger.error(f"Error in PDF OCR: {e}")
        raise


def _parse_image_with_ocr(image_path: Path) -> str:
    """
    Extract text from a single image using OCR.
    
    Args:
        image_path: Path to image file
        
    Returns:
        OCR-extracted text
    """
    logger.info(f"OCR processing image: {image_path.name}")
    
    try:
        # Open image
        image = Image.open(image_path)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(
            image,
            lang='eng',
            config='--psm 3'
        )
        
        logger.info(f"OCR extracted {len(text)} characters from image")
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error in image OCR: {e}")
        raise


def parse_with_ocr_and_vision(file_path: str | Path, ollama_url: str = "http://localhost:11434") -> str:
    """
    Advanced parser that combines OCR with AI vision model for image description.
    
    This parser:
    1. Extracts text using OCR
    2. Detects images in the document
    3. Uses Ollama vision models (llava, bakllava) to describe images
    4. Combines text + image descriptions
    
    Args:
        file_path: Path to the document file
        ollama_url: URL to Ollama API server
        
    Returns:
        Combined text and image descriptions
    """
    try:
        file_path = Path(file_path)
        logger.info(f"Starting OCR + Vision parsing for {file_path.name}")
        
        # First, get OCR text
        ocr_text = parse_with_ocr(file_path)
        
        # Then, get image descriptions
        image_descriptions = _describe_images_with_vision(file_path, ollama_url)
        
        # Combine results
        if image_descriptions:
            combined_text = f"{ocr_text}\n\n{'='*50}\n"
            combined_text += "IMAGE DESCRIPTIONS (AI Generated):\n"
            combined_text += "="*50 + "\n\n"
            combined_text += "\n\n".join(image_descriptions)
            return combined_text
        else:
            return ocr_text
            
    except Exception as e:
        logger.error(f"Error in OCR + Vision parsing: {e}")
        # Fallback to OCR only
        return parse_with_ocr(file_path)


def _describe_images_with_vision(file_path: Path, ollama_url: str) -> List[str]:
    """
    Use Ollama vision model to generate descriptions of images.
    
    Args:
        file_path: Path to PDF or image file
        ollama_url: URL to Ollama API
        
    Returns:
        List of image descriptions
    """
    try:
        # Check if vision model is available
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code != 200:
            logger.warning("Cannot connect to Ollama, skipping vision descriptions")
            return []
        
        models = response.json().get('models', [])
        vision_models = [m for m in models if 'llava' in m.get('name', '').lower() or 'bakllava' in m.get('name', '').lower()]
        
        if not vision_models:
            logger.warning("No vision models (llava/bakllava) available in Ollama")
            return []
        
        vision_model = vision_models[0]['name']
        logger.info(f"Using vision model: {vision_model}")
        
        # Convert PDF pages or single image to image files
        file_ext = file_path.suffix.lower()
        descriptions = []
        
        if file_ext == '.pdf':
            # Convert PDF to images
            images = convert_from_path(str(file_path), dpi=150)  # Lower DPI for vision (faster)
            
            for page_num, image in enumerate(images[:5], start=1):  # Limit to first 5 pages
                desc = _get_image_description(image, vision_model, ollama_url, f"Page {page_num}")
                if desc:
                    descriptions.append(desc)
        else:
            # Single image
            image = Image.open(file_path)
            desc = _get_image_description(image, vision_model, ollama_url, file_path.name)
            if desc:
                descriptions.append(desc)
        
        return descriptions
        
    except Exception as e:
        logger.error(f"Error describing images with vision model: {e}")
        return []


def _get_image_description(image: Image.Image, model: str, ollama_url: str, image_label: str) -> str:
    """
    Get AI description of a single image using Ollama vision model.
    
    Args:
        image: PIL Image object
        model: Vision model name
        ollama_url: Ollama API URL
        image_label: Label for the image (e.g., "Page 1")
        
    Returns:
        AI-generated description of the image
    """
    try:
        import base64
        from io import BytesIO
        
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Call Ollama vision API
        payload = {
            "model": model,
            "prompt": "Describe this image in detail. Include any text, diagrams, charts, tables, or important visual elements you see.",
            "images": [img_base64],
            "stream": False
        }
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            description = result.get('response', '').strip()
            logger.info(f"Generated description for {image_label}: {len(description)} chars")
            return f"[{image_label}] {description}"
        else:
            logger.warning(f"Failed to get description for {image_label}: {response.status_code}")
            return ""
            
    except Exception as e:
        logger.error(f"Error getting image description: {e}")
        return ""


# Alias for main parsing function
def parse(file_path: str) -> str:
    """
    Main entry point for OCR parser.
    Uses OCR only (no vision model) for faster processing.
    """
    return parse_with_ocr(file_path)
