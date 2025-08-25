# AI Excel Translation System

This system converts Excel files to JSON parts and translates them using Google's Gemini AI model.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the project root with your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
   
   Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

### 1. Convert Excel to JSON Parts

```python
from json_converter import convert_excel_to_json_parts

# Convert with default settings (500 items per part, japanese folder)
convert_excel_to_json_parts()

# Custom configuration
convert_excel_to_json_parts(items_per_part=1000, language="english")
```

### 2. Translate Single JSON File

```python
from translate import translate_single_json_file

# Translate p1.json from parts/japanese/ to output/japanese/
success = translate_single_json_file("japanese", "p1")
```

### 3. Translate All JSON Files

```python
from translate import translate_all_json_files

# Translate all files in parts/japanese/ to output/japanese/
success = translate_all_json_files("japanese")
```

### 4. Check Translation Status

```python
from translate import get_translation_status

# Get status for japanese language
status = get_translation_status("japanese")
print(f"Source files: {status['total_source']}")
print(f"Translated: {status['total_translated']}")
print(f"Pending: {status['total_pending']}")
```

## File Structure

```
ai-xslx-translation/
├── source/
│   └── Output_Final.xlsx          # Source Excel file
├── parts/
│   └── japanese/                  # JSON parts (p1.json, p2.json, etc.)
├── output/
│   └── japanese/                  # Translated JSON files
├── json_converter.py              # Excel to JSON conversion
├── translate.py                   # Translation system
└── requirements.txt               # Python dependencies
```

## Features

- **AI-Powered Translation**: Uses Google Gemini Pro model for high-quality translations
- **LangGraph Integration**: Advanced workflow management with LangGraph
- **Batch Processing**: Translate single files or entire language folders
- **Progress Tracking**: Monitor translation progress and status
- **Error Handling**: Robust error handling with fallback mechanisms
- **UTF-8 Support**: Full support for international characters

## Example Workflow

1. **Convert Excel to parts:**
   ```bash
   python json_converter.py
   ```

2. **Translate all parts:**
   ```bash
   python translate.py
   ```

3. **Check results in output/japanese/ folder**

## Notes

- The system only translates non-empty values (empty strings are preserved)
- Each translation request uses the Gemini API (may incur costs)
- Translation quality depends on the source text complexity
- The system automatically creates necessary directories
