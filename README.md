# AI Excel Translation System

This system converts Excel/JSON files to JSON parts and translates them using Google's Gemini AI model.

## Setup
1. Install python virtual environment
   ```bash
   python -m venv .venv
   ```
2. Active virtual environment
   
   Linux:
   ```bash
   source .venv/bin/activate
   ```

   Windows:

   ```bash
   .venv/Scripts/Activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root with your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
   
   Get your API key from: [Google AI Studio](https://aistudio.google.com/app/apikey)

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

**Run Full Pipeline for JSON file (JSON → JSON → Translate → Merge):**
```bash
python main.py -c true  --full
python main.py -c true --language japanese --max-lines-per-part 500 --full
```
**If you want to run full pipeline without converting JSON/Excel file to smaller parts**
```bash
python main.py --full
python main.py --language chinese --max-lines-per-part 500 --full
```

**Run Full Pipeline for Excel file (Excel → JSON → Translate → Merge):**
```bash
python main.py -c true --full -t excel
python main.py -c true --language japanese --items-per-part 200 --full -t excel
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
