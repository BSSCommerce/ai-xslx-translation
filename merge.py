import json
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_json_files_to_xlsx(language: str) -> bool:
    """
    Merge all JSON files in output/{language} folder to a single Excel file.
    
    Args:
        language (str): Language folder name (e.g., "japanese")
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Define paths
        input_dir = Path("output") / language
        output_file = input_dir / "final.xlsx"
        
        # Check if input directory exists
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return False
        
        # Get all JSON files in the directory
        json_files = list(input_dir.glob("*.json"))
        
        # Filter out the final.xlsx file if it exists
        json_files = [f for f in json_files if f.name != "final.xlsx"]
        
        if not json_files:
            logger.warning(f"No JSON files found in {input_dir}")
            return False
        
        logger.info(f"Found {len(json_files)} JSON files to merge")
        
        # Dictionary to store all key-value pairs
        all_data = {}
        file_stats = {}
        
        # Process each JSON file
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Count items in this file
                item_count = len(data)
                file_stats[json_file.name] = item_count
                
                # Add data to the main dictionary
                # If there are duplicate keys, the later file will overwrite earlier ones
                all_data.update(data)
                
                logger.info(f"Processed {json_file.name}: {item_count} items")
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing {json_file.name}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error reading {json_file.name}: {str(e)}")
                continue
        
        if not all_data:
            logger.error("No valid data found in any JSON files")
            return False
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {"Key": key, "Value": value} 
            for key, value in all_data.items()
        ])
        
        # Sort by key for better organization
        df = df.sort_values("Key").reset_index(drop=True)
        
        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Translations', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total JSON files processed',
                    'Total unique keys',
                    'Total values',
                    'Output file'
                ],
                'Value': [
                    len(json_files),
                    len(all_data),
                    len(all_data),
                    str(output_file)
                ]
            }
            
            # File details
            for filename, count in file_stats.items():
                summary_data['Metric'].append(f'Items in {filename}')
                summary_data['Value'].append(count)
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 100)  # Cap at 100 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logger.info(f"Successfully merged {len(json_files)} JSON files into {output_file}")
        logger.info(f"Total unique keys: {len(all_data)}")
        
        # Print summary
        print(f"\n📊 Merge Summary for {language}:")
        print(f"   JSON files processed: {len(json_files)}")
        print(f"   Total unique keys: {len(all_data)}")
        print(f"   Output file: {output_file}")
        print(f"   File sizes:")
        for filename, count in file_stats.items():
            print(f"     {filename}: {count} items")
        
        return True
        
    except Exception as e:
        logger.error(f"Error merging JSON files: {str(e)}")
        return False

def get_merge_status(language: str) -> Dict:
    """
    Get the status of JSON files in a language folder.
    
    Args:
        language (str): Language folder name
    
    Returns:
        dict: Status information
    """
    try:
        input_dir = Path("output") / language
        output_file = input_dir / "final.xlsx"
        
        status = {
            "language": language,
            "input_directory": str(input_dir),
            "output_file": str(output_file),
            "json_files": [],
            "total_items": 0,
            "final_xlsx_exists": False,
            "can_merge": False
        }
        
        if not input_dir.exists():
            return status
        
        # Get JSON files
        json_files = list(input_dir.glob("*.json"))
        json_files = [f for f in json_files if f.name != "final.xlsx"]
        
        status["json_files"] = [f.name for f in json_files]
        status["total_files"] = len(json_files)
        
        # Check if final.xlsx exists
        status["final_xlsx_exists"] = output_file.exists()
        
        # Count total items
        total_items = 0
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_items += len(data)
            except:
                continue
        
        status["total_items"] = total_items
        status["can_merge"] = len(json_files) > 0
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting merge status: {str(e)}")
        return {"error": str(e)}

def merge_all_languages() -> Dict[str, bool]:
    """
    Merge JSON files for all available languages.
    
    Returns:
        dict: Results for each language
    """
    try:
        output_dir = Path("output")
        if not output_dir.exists():
            logger.error("Output directory not found")
            return {}
        
        # Get all language directories
        language_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
        results = {}
        
        for lang_dir in language_dirs:
            language = lang_dir.name
            logger.info(f"Processing language: {language}")
            success = merge_json_files_to_xlsx(language)
            results[language] = success
        
        return results
        
    except Exception as e:
        logger.error(f"Error merging all languages: {str(e)}")
        return {}

if __name__ == "__main__":
    print("JSON to Excel Merger")
    print("=" * 40)
    
    # Example: Merge Japanese files
    print("\n1. Merging Japanese JSON files...")
    success = merge_json_files_to_xlsx("japanese")
    print(f"Merge result: {'Success' if success else 'Failed'}")
    
    # Example: Get merge status
    print("\n2. Merge status:")
    status = get_merge_status("japanese")
    if 'error' not in status:
        print(f"Language: {status['language']}")
        print(f"JSON files: {status['total_files']}")
        print(f"Total items: {status['total_items']}")
        print(f"Final XLSX exists: {status['final_xlsx_exists']}")
        print(f"Can merge: {status['can_merge']}")
    else:
        print(f"Error: {status['error']}")
    
    # Example: Merge all languages
    print("\n3. Merging all languages...")
    all_results = merge_all_languages()
    for lang, result in all_results.items():
        print(f"  {lang}: {'✓' if result else '✗'}")
