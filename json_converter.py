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


def convert_json_to_parts(max_lines_per_part=500, language="japanese"):
    """
    Convert large JSON file to multiple smaller JSON parts based on line counts.
    
    Args:
        input_file (str): Path to the input JSON file, default "source/en.default.schema.json"
        max_lines_per_part (int): Maximum lines per JSON part, default 500
        output_folder (str): Output folder for parts, default "parts"
    
    Returns:
        list: List of created JSON file paths
    """
    import json
    from pathlib import Path

    input_file="source/en.default.schema.json"
    # Create output folder if it doesn't exist
    output_path = Path("parts") / language
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get all lines to analyze structure
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find section boundaries by analyzing the JSON structure
        sections = []
        current_section = None
        current_start_line = 0
        
        for i, line in enumerate(lines):
            # Look for top-level sections (keys at root level)
            stripped = line.strip()
            if stripped.startswith('"') and stripped.endswith(': {') and not line.startswith('    '):
                # This is a top-level section
                if current_section:
                    sections.append({
                        'name': current_section,
                        'start_line': current_start_line,
                        'end_line': i - 1,
                        'line_count': i - current_start_line
                    })
                
                # Extract section name
                section_name = stripped.split('"')[1]
                current_section = section_name
                current_start_line = i
        
        # Add the last section
        if current_section:
            sections.append({
                'name': current_section,
                'start_line': current_start_line,
                'end_line': len(lines) - 1,
                'line_count': len(lines) - current_start_line
            })
        
        print(f"Found {len(sections)} sections:")
        for section in sections:
            print(f"  - {section['name']}: {section['line_count']} lines")
        
        # Group sections to keep total lines under max_lines_per_part
        grouped_sections = []
        current_group = []
        current_group_lines = 0
        
     
        for section in sections:
            # If adding this section would exceed the limit, start a new group
            if (current_group_lines + section['line_count'] > max_lines_per_part) and current_group:
                grouped_sections.append(current_group)
                current_group = [section]
                current_group_lines = section['line_count']
            else:
                current_group.append(section)
                current_group_lines += section['line_count']
        
        # Add the last group if it has sections
        if current_group:
            grouped_sections.append(current_group)
       
        print(f"\nGrouped into {len(grouped_sections)} parts:")
        for i, group in enumerate(grouped_sections):
            total_lines = sum(s['line_count'] for s in group)
            section_names = [s['name'] for s in group]
            print(f"  Part {i+1}: {total_lines} lines - {', '.join(section_names)}")
        
        # Create JSON parts
        json_files = []
        for part_num, group in enumerate(grouped_sections, 1):
            # Create JSON object for this part
            part_data = {}
            for section in group:
                section_name = section['name']
                if section_name in data:
                    part_data[section_name] = data[section_name]
            
            # Create filename
            filename = f"p{part_num}.json"
            filepath = output_path / filename
            
            # Write JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(part_data, f, ensure_ascii=False, indent=2)
            
            json_files.append(str(filepath))
            total_lines = sum(s['line_count'] for s in group)
            print(f"Created {filepath} with {len(group)} sections ({total_lines} lines)")
        
        print(f"\nConversion complete! Created {len(grouped_sections)} JSON parts in {output_path}")
        print(f"Total sections processed: {len(sections)}")
        
        return json_files
        
    except FileNotFoundError:
        print(f"Error: JSON file '{input_file}' not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{input_file}': {str(e)}")
        return []
    except Exception as e:
        print(f"Error converting JSON file: {str(e)}")
        return []


if __name__ == "__main__":
    # Example usage
    # print("Converting Excel to JSON parts...")
    # result = convert_excel_to_json_parts(200, "espanol")
    # print(f"Created files: {result}")
    
    print("\n" + "="*50)
    print("Converting JSON schema to parts...")
    schema_result = convert_json_to_parts()
    print(f"Created schema files: {schema_result}")
