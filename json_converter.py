import pandas as pd
import json
import os
from pathlib import Path


def convert_excel_to_json_parts(items_per_part=200, language="japanese"):
    """
    Convert Output_Final.xlsx to multiple JSON parts.
    
    Args:
        items_per_part (int): Number of items per JSON part, default 200
        language (str): Language folder name, default "japanese"
    
    Returns:
        list: List of created JSON file paths
    """
    # Define file paths
    excel_file = "source/Output_Final.xlsx"
    parts_folder = Path("parts") / language
    
    # Create parts folder if it doesn't exist
    parts_folder.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        # Get the first column as keys
        if df.empty:
            print("Excel file is empty")
            return []
        
        keys = df.iloc[:, 0].tolist()
        
        # Create JSON parts
        json_files = []
        total_items = len(keys)
        total_parts = (total_items + items_per_part - 1) // items_per_part  # Ceiling division
        
        for part_num in range(1, total_parts + 1):
            start_idx = (part_num - 1) * items_per_part
            end_idx = min(start_idx + items_per_part, total_items)
            
            # Create JSON object for this part
            part_data = {}
            for key in keys[start_idx:end_idx]:
                if pd.isna(key):  # Handle NaN values
                    part_data[str(key)] = ""
                else:
                    part_data[str(key)] = ""
            
            # Create filename
            filename = f"p{part_num}.json"
            filepath = parts_folder / filename
            
            # Write JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(part_data, f, ensure_ascii=False, indent=2)
            
            json_files.append(str(filepath))
            print(f"Created {filepath} with {len(part_data)} items")
        
        print(f"\nConversion complete! Created {total_parts} JSON parts in {parts_folder}")
        print(f"Total items processed: {total_items}")
        
        return json_files
        
    except FileNotFoundError:
        print(f"Error: Excel file '{excel_file}' not found")
        return []
    except Exception as e:
        print(f"Error converting Excel file: {str(e)}")
        return []


if __name__ == "__main__":
    # Example usage
    print("Converting Excel to JSON parts...")
    result = convert_excel_to_json_parts(200, "japanese")
    print(f"Created files: {result}")
