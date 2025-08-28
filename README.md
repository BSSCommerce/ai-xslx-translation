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

## Core Modules

### 1. Main Pipeline (`main.py`)

The main pipeline orchestrates the entire translation workflow from Excel to final translated Excel file.

#### Features
- **Unified Workflow**: Combines all translation steps into one command
- **Flexible Execution**: Run full pipeline or single file translation
- **Status Monitoring**: Real-time pipeline status and progress tracking
- **Error Handling**: Comprehensive error handling with detailed logging
- **Batch Processing**: Process entire language folders or individual files

#### Usage Examples

**Show Pipeline Status:**
```bash
python main.py --status
python main.py -s
```

**Run Full Pipeline (Excel → JSON → Translate → Merge):**
```bash
python main.py --full
python main.py --language japanese --items-per-part 200 --full
```

**Translate Single File:**
```bash
python main.py --file p1
python main.py -f p1 --language spanish
```

**Custom Configuration:**
```bash
# Set language and items per part
python main.py --language spanish --items-per-part 300

# Convert Excel to JSON parts first, then translate single file
python main.py --file p1 --convert-to-json
```

#### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--language` | `-l` | Target language for translation | `japanese` |
| `--items-per-part` | `-i` | Number of items per JSON part | `200` |
| `--file` | `-f` | Translate single file (without extension) | None |
| `--status` | `-s` | Show pipeline status only | False |
| `--convert-to-json` | `-c` | Convert Excel to JSON parts first | False |
| `--full` | | Run complete pipeline | False |

#### Pipeline Status Indicators

The system provides real-time status updates with these indicators:

- **✅ Complete**: All steps finished, final Excel created
- **🔄 Translated Ready to Merge**: Translation complete, ready for final merge
- **📋 Parts Ready to Translate**: JSON parts created, ready for translation
- **📁 Ready to Convert**: Excel source ready for JSON conversion
- **❌ No Source**: Excel source file not found

#### Example Output

```bash
📊 Pipeline Status for japanese
==================================================
Overall Status: ✅ Complete
📁 Excel Source: ✅ source/Output_Final.xlsx
📋 JSON Parts: ✅ 12 files
   - p1.json
   - p2.json
   - p3.json
   - p4.json
   - p5.json
   ... and 7 more
🌐 Translation: 12/12 files
📊 Final Excel: ✅ Created
```

### 2. Text to JSON Converter (`text_to_json.py`)

This module cleans and converts AI translation responses to clean JSON format, handling common artifacts and formatting issues.

#### Features
- **AI Response Cleaning**: Removes markdown formatting and common AI artifacts
- **Batch Processing**: Process multiple translation files at once
- **Error Recovery**: Robust error handling with detailed logging
- **Format Validation**: Ensures output is valid JSON
- **Flexible Input**: Handles various AI response formats

#### Core Functions

**`clean_ai_response_to_json(ai_response: str) -> str`**
- Converts Google AI's markdown-wrapped JSON responses to clean JSON
- Handles both ```json and ``` code block formats
- Falls back to using entire response if no code blocks found

**`clean_common_artifacts(content: str) -> str`**
- Removes common AI response prefixes/suffixes
- Cleans extra whitespace and newlines
- Extracts JSON object boundaries

**`process_translation_file(input_file: str, output_file: str = None) -> dict`**
- Processes a single translation file
- Generates cleaned output filename automatically
- Returns processing results with error handling

**`batch_process_translations(input_dir: str, output_dir: str = None) -> list`**
- Processes all translation files in a directory
- Creates organized output structure
- Returns comprehensive processing results

#### Usage Examples

**Process Single File:**
```python
from text_to_json import process_translation_file

# Process with auto-generated output filename
result = process_translation_file("output/japanese/p1.json")

# Process with custom output filename
result = process_translation_file("output/japanese/p1.json", "cleaned/p1_clean.json")
```

**Batch Process Directory:**
```python
from text_to_json import batch_process_translations

# Process all files in output/japanese/
results = batch_process_translations("output/japanese")

# Process with custom output directory
results = batch_process_translations("output/japanese", "cleaned/japanese")
```

**Direct Function Usage:**
```python
from text_to_json import clean_ai_response_to_json, clean_common_artifacts

# Clean AI response
cleaned_json = clean_ai_response_to_json(ai_response_text)

# Clean common artifacts
final_content = clean_common_artifacts(cleaned_json)
```

#### Command Line Usage

```bash
# Process single file
python text_to_json.py

# The script includes example usage for:
# - Single file processing: output/japanese/p1.json
# - Batch processing: output/japanese/ directory
```

#### Input/Output Handling

**Input Formats Supported:**
- Raw AI responses with markdown code blocks
- Plain text responses
- JSON with extra formatting
- Mixed content with AI artifacts

**Output Features:**
- Clean, valid JSON format
- Organized file structure
- Error logging and reporting
- Processing status tracking

**Example Input (AI Response):**
```markdown
Here is the translation:

```json
{
  "key1": "translated_value1",
  "key2": "translated_value2"
}
```

The translation is complete.
```

**Example Output (Cleaned JSON):**
```json
{
  "key1": "translated_value1",
  "key2": "translated_value2"
}
```

## Complete Workflow Examples

### Basic Translation Workflow

1. **Check current status:**
   ```bash
   python main.py --status
   ```

2. **Run full pipeline:**
   ```bash
   python main.py --full
   ```

3. **Monitor progress and check final results**

### Single File Translation Workflow

1. **Translate specific file:**
   ```bash
   python main.py --file p3 --language spanish
   ```

2. **Check translation status:**
   ```bash
   python main.py --status
   ```

3. **Merge to final Excel:**
   ```bash
   python main.py --full  # This will skip conversion and translation, just merge
   ```

### Custom Configuration Workflow

1. **Set custom parameters:**
   ```bash
   python main.py --language french --items-per-part 150
   ```

2. **Convert Excel to JSON parts:**
   ```bash
   python main.py --file p1 --convert-to-json
   ```

3. **Translate and merge:**
   ```bash
   python main.py --full
   ```

## File Structure

```
ai-xslx-translation/
├── source/
│   └── Output_Final.xlsx          # Source Excel file
├── parts/
│   ├── japanese/                  # JSON parts (p1.json, p2.json, etc.)
│   ├── spanish/                   # Language-specific parts
│   └── french/                    # Language-specific parts
├── output/
│   ├── japanese/                  # Translated JSON files
│   ├── spanish/                   # Translated JSON files
│   └── french/                    # Translated JSON files
├── main.py                        # Main pipeline orchestrator
├── text_to_json.py                # AI response cleaner and JSON converter
├── json_converter.py              # Excel to JSON conversion
├── translate.py                   # Translation system
├── merge.py                       # JSON to Excel merger
├── translation_pipeline.log       # Pipeline execution logs
└── requirements.txt               # Python dependencies
```

## Features

- **AI-Powered Translation**: Uses Google Gemini Pro model for high-quality translations
- **LangGraph Integration**: Advanced workflow management with LangGraph
- **Unified Pipeline**: Single command execution for complete workflows
- **Flexible Processing**: Support for single files or batch operations
- **Real-time Status**: Live pipeline status monitoring and progress tracking
- **Batch Processing**: Translate single files or entire language folders
- **Error Handling**: Robust error handling with fallback mechanisms
- **UTF-8 Support**: Full support for international characters
- **Logging**: Comprehensive logging for debugging and monitoring
- **Configuration**: Flexible language and batch size configuration

## Error Handling and Troubleshooting

### Common Issues

1. **Missing API Key:**
   ```
   ❌ ERROR: GEMINI_API_KEY not found in .env file
   ```
   **Solution:** Create `.env` file with your Gemini API key

2. **File Not Found:**
   ```
   ❌ Source file not found: parts/japanese/p1.json
   ```
   **Solution:** Run with `--convert-to-json` first or check file paths

3. **Translation Failures:**
   - Check API key validity
   - Verify internet connection
   - Check API rate limits

### Logging and Debugging

- **Log File:** `translation_pipeline.log` contains detailed execution logs
- **Console Output:** Real-time status updates and error messages
- **Verbose Logging:** Set logging level in main.py for detailed debugging

## Performance Considerations

- **Batch Sizes:** Larger `items-per-part` values reduce API calls but increase memory usage
- **API Limits:** Monitor Gemini API usage and rate limits
- **File Processing:** Large Excel files are automatically split into manageable parts
- **Memory Usage:** JSON parts are processed sequentially to minimize memory footprint

## Notes

- The system only translates non-empty values (empty strings are preserved)
- Each translation request uses the Gemini API (may incur costs)
- Translation quality depends on the source text complexity
- The system automatically creates necessary directories
- All operations are logged for audit and debugging purposes
- The pipeline can be resumed from any step if interrupted
