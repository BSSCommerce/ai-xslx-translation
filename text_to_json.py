import json
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_ai_response_to_json(ai_response: str) -> str:
    """
    Convert Google AI's markdown-wrapped JSON response to clean JSON format.
    
    Args:
        ai_response (str): The raw response from Google AI (may contain markdown formatting)
        output_file (str): Optional output file path to save the cleaned JSON
    
    Returns:
        dict: Cleaned JSON data
    """
    try:
        # Remove markdown code blocks if present
        # Pattern to match ```json ... ``` or ``` ... ```
        markdown_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        match = re.search(markdown_pattern, ai_response, re.DOTALL)
        
        if match:
            # Extract content between code blocks
            json_content = match.group(1).strip()
            logger.info("Found markdown code blocks, extracted JSON content")
        else:
            # No markdown blocks found, use the entire response
            json_content = ai_response.strip()
            logger.info("No markdown blocks found, using entire response")
        
       
    
        
        return json_content
        
    except Exception as e:
        logger.error(f"Error cleaning AI response: {str(e)}")
        return ""

def clean_common_artifacts(content: str) -> str:
    """
    Clean common artifacts that AI responses might include.
    
    Args:
        content (str): Raw content to clean
    
    Returns:
        str: Cleaned content
    """
    # Remove common AI response prefixes/suffixes
    content = re.sub(r'^Here is the translation.*?:?\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'^Translation.*?:?\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\s*The translation is complete.*$', '', content, flags=re.IGNORECASE)
    
    # Remove extra whitespace and newlines
    content = re.sub(r'\n\s*\n', '\n', content)
    content = content.strip()
    
    # Try to find JSON object boundaries
    json_start = content.find('{')
    json_end = content.rfind('}')
    
    if json_start != -1 and json_end != -1 and json_end > json_start:
        content = content[json_start:json_end + 1]
    
    return content

def process_translation_file(input_file: str, output_file: str = None) -> dict:
    """
    Process a translation file and convert it to clean JSON.
    
    Args:
        input_file (str): Path to the input file containing AI response
        output_file (str): Optional output file path (defaults to input_file_cleaned.json)
    
    Returns:
        dict: Cleaned JSON data
    """
    try:
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Read the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate output filename if not provided
        if not output_file:
            output_file = str(input_path.parent / f"{input_path.stem}_cleaned.json")
        
        # Clean and convert the content
        cleaned_data = clean_ai_response_to_json(content, output_file)
        
        return cleaned_data
        
    except Exception as e:
        logger.error(f"Error processing translation file: {str(e)}")
        return {"error": str(e)}

def batch_process_translations(input_dir: str, output_dir: str = None) -> list:
    """
    Process all translation files in a directory.
    
    Args:
        input_dir (str): Directory containing translation files
        output_dir (str): Optional output directory (defaults to input_dir/cleaned)
    
    Returns:
        list: List of processed file results
    """
    try:
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Set output directory
        if not output_dir:
            output_dir = str(input_path / "cleaned")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all JSON files
        json_files = list(input_path.glob("*.json"))
        results = []
        
        for json_file in json_files:
            output_file = str(output_path / f"{json_file.stem}_cleaned.json")
            result = process_translation_file(str(json_file), output_file)
            result["input_file"] = str(json_file)
            result["output_file"] = output_file
            results.append(result)
        
        logger.info(f"Processed {len(results)} files")
        return results
        
    except Exception as e:
        logger.error(f"Error batch processing translations: {str(e)}")
        return [{"error": str(e)}]

if __name__ == "__main__":
    # Example usage
    print("AI Response to JSON Converter")
    print("=" * 40)
    
    # Example: Process a single file
    input_file = "output/japanese/p1.json"
    if Path(input_file).exists():
        print(f"\nProcessing: {input_file}")
        result = process_translation_file(input_file)
        print(f"Success: {'error' not in result}")
        if 'error' not in result:
            print(f"Keys found: {len(result)}")
            print(f"Sample keys: {list(result.keys())[:5]}")
    else:
        print(f"File not found: {input_file}")
    
    # Example: Batch process all files in output/japanese/
    print(f"\nBatch processing output/japanese/ directory...")
    results = batch_process_translations("output/japanese")
    
    for result in results:
        if 'error' not in result:
            print(f"✓ {result['input_file']} -> {result['output_file']}")
        else:
            print(f"✗ {result['input_file']}: {result['error']}")
