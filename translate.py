import json
import os
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import logging
from text_to_json import clean_ai_response_to_json, clean_common_artifacts
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Translation agent
class TranslationAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=1
        )
    
    async def translate(self, source_text: str, target_language: str) -> str:
        """Translate text using the AI model"""
        try:
            if not source_text or not source_text.strip():
                return source_text
            # Create translation prompt
            prompt = f"""
            Input text use JSON format. for example:
            {{
                "text to translate": ""
            }}
            replace "" with the translated text.

            Translate the following text to {target_language}. 
            Maintain the original meaning and context. 
            Return only the translated text, nothing else.

            
            Text to translate: {source_text}
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return source_text  # Return original text if translation fails

def translate_single_json_file(language: str, file_name: str) -> bool:
    """
    Translate a single JSON file based on language and file name.
    
    Args:
        language (str): Language folder name (e.g., "japanese")
        file_name (str): File name without extension (e.g., "p1")
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Define file paths
        source_file = Path("parts") / language / f"{file_name}.json"
        output_dir = Path("output") / language
        output_file = output_dir / f"{file_name}.json"
        
        # Check if source file exists
        if not source_file.exists():
            logger.error(f"Source file not found: {source_file}")
            return False
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load source JSON
        with open(source_file, 'r', encoding='utf-8') as f:
            # Load string from file
            source_data: str = f.read()
        
        logger.info(f"Translating {source_file} to {language}")
        
        # Initialize translation agent
        agent = TranslationAgent()
        

        translated_value = asyncio.run(agent.translate(source_data, language))
               
        
        # Save translated data
        with open(output_file, 'w', encoding='utf-8') as f:
            translated_value = clean_ai_response_to_json(translated_value)
            translated_value = clean_common_artifacts(translated_value)
            f.write(translated_value)
        
        logger.info(f"Translation complete: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error translating single file: {str(e)}")
        return False

def translate_all_json_files(language: str) -> bool:
    """
    Translate all JSON files in the specified language folder.
    
    Args:
        language (str): Language folder name (e.g., "japanese")
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        parts_dir = Path("parts") / language
        output_dir = Path("output") / language
        
        # Check if parts directory exists
        if not parts_dir.exists():
            logger.error(f"Parts directory not found: {parts_dir}")
            return False
        
        # Get all JSON files
        json_files = list(parts_dir.glob("*.json"))
        if not json_files:
            logger.warning(f"No JSON files found in {parts_dir}")
            return True
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Found {len(json_files)} JSON files to translate")
        
        # Translate each file
        success_count = 0
        for json_file in json_files:
            file_name = json_file.stem  # Get filename without extension
            if translate_single_json_file(language, file_name):
                success_count += 1
            else:
                logger.error(f"Failed to translate {file_name}")
        
        logger.info(f"Translation complete: {success_count}/{len(json_files)} files successful")
        return success_count == len(json_files)
        
    except Exception as e:
        logger.error(f"Error translating all files: {str(e)}")
        return False

def get_translation_status(language: str) -> Dict[str, Any]:
    """
    Get the status of translation files for a specific language.
    
    Args:
        language (str): Language folder name
    
    Returns:
        dict: Status information
    """
    try:
        parts_dir = Path("parts") / language
        output_dir = Path("output") / language
        
        status = {
            "language": language,
            "source_files": [],
            "translated_files": [],
            "pending_files": [],
            "total_source": 0,
            "total_translated": 0,
            "total_pending": 0
        }
        
        # Get source files
        if parts_dir.exists():
            source_files = list(parts_dir.glob("*.json"))
            status["source_files"] = [f.stem for f in source_files]
            status["total_source"] = len(source_files)
        
        # Get translated files
        if output_dir.exists():
            translated_files = list(output_dir.glob("*.json"))
            status["translated_files"] = [f.stem for f in translated_files]
            status["total_translated"] = len(translated_files)
        
        # Calculate pending files
        status["pending_files"] = list(set(status["source_files"]) - set(status["translated_files"]))
        status["total_pending"] = len(status["pending_files"])
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting translation status: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Example usage
    print("Translation System")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not found in .env file")
        print("Please create a .env file with your Gemini API key")
        exit(1)
    
    # Example: Translate single file
    print("\n1. Translating single file (p1.json)...")
    success = translate_single_json_file("japanese", "p1")
    print(f"Single file translation: {'Success' if success else 'Failed'}")
    
    # # Example: Translate all files
    # print("\n2. Translating all files...")
    # success = translate_all_json_files("japanese")
    # print(f"All files translation: {'Success' if success else 'Failed'}")
    
    # Example: Get status
    print("\n3. Translation status:")
    status = get_translation_status("japanese")
    print(f"Language: {status['language']}")
    print(f"Source files: {status['total_source']}")
    print(f"Translated files: {status['total_translated']}")
    print(f"Pending files: {status['total_pending']}")
