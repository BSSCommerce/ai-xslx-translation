#!/usr/bin/env python3
"""
AI Excel Translation Pipeline
Combines JSON conversion, translation, and merging into one unified workflow.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Import our modules
from json_converter import convert_excel_to_json_parts
from translate import translate_single_json_file, translate_all_json_files, get_translation_status
from merge import merge_json_files_to_xlsx, get_merge_status
from text_to_json import process_translation_file

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TranslationPipeline:
    """Main translation pipeline that orchestrates all steps."""
    
    def __init__(self, language: str = "japanese", items_per_part: int = 500):
        self.language = language
        self.items_per_part = items_per_part
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    def run_full_pipeline(self, clean_output: bool = False) -> Dict:
        """
        Run the complete translation pipeline from Excel to final Excel.
        
        Args:
            clean_output (bool): Whether to clean existing output files
            
        Returns:
            dict: Pipeline execution results
        """
        results = {
            "pipeline": "full",
            "language": self.language,
            "steps": {},
            "success": False,
            "errors": []
        }
        
        try:
            logger.info(f"🚀 Starting full translation pipeline for {self.language}")
            
            # Step 1: Convert Excel to JSON parts
            logger.info("📋 Step 1: Converting Excel to JSON parts...")
            json_files = convert_excel_to_json_parts(self.items_per_part, self.language)
            if not json_files:
                results["errors"].append("Failed to convert Excel to JSON parts")
                return results
            results["steps"]["json_conversion"] = {"success": True, "files": json_files}
            logger.info(f"✅ Step 1 complete: {len(json_files)} JSON parts created")
            
            # Step 2: Translate all JSON files
            logger.info("🌐 Step 2: Translating all JSON files...")
            translation_success = translate_all_json_files(self.language)
            if not translation_success:
                results["errors"].append("Failed to translate JSON files")
                return results
            results["steps"]["translation"] = {"success": True}
            logger.info("✅ Step 2 complete: All files translated")
            
            # Step 3: Merge to final Excel
            logger.info("📊 Step 3: Merging to final Excel...")
            merge_success = merge_json_files_to_xlsx(self.language)
            if not merge_success:
                results["errors"].append("Failed to merge JSON files")
                return results
            results["steps"]["merging"] = {"success": True}
            logger.info("✅ Step 3 complete: Final Excel created")
            
            results["success"] = True
            logger.info(f"🎉 Full pipeline completed successfully for {self.language}")
            
        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    def run_single_file_pipeline(self, file_name: str, convert_to_json: bool = False) -> Dict:
        """
        Run translation pipeline for a single file.
        
        Args:
            file_name (str): Name of the file to translate (without extension)
            convert_to_json (bool): Whether to convert Excel to JSON parts
            
        Returns:
            dict: Pipeline execution results
        """
        results = {
            "pipeline": "single_file",
            "language": self.language,
            "file_name": file_name,
            "steps": {},
            "success": False,
            "errors": []
        }
        
        try:
            logger.info(f"🚀 Starting single file translation pipeline for {file_name}")
            

            # Step 1: Convert Excel to JSON parts
            if convert_to_json:
                logger.info("📋 Step 1: Converting Excel to JSON parts...")
                json_files = convert_excel_to_json_parts(self.items_per_part, self.language)
                if not json_files:
                    results["errors"].append("Failed to convert Excel to JSON parts")
                    return results
                results["steps"]["json_conversion"] = {"success": True, "files": json_files}
                logger.info(f"✅ Step 1 complete: {len(json_files)} JSON parts created")
            else:
                logger.info("📋 Step 1: Skipping Excel to JSON parts conversion")

            # Check if JSON parts exist
            parts_dir = Path("parts") / self.language
            if not parts_dir.exists():
                results["errors"].append(f"Parts directory not found: {parts_dir}")
                return results
            
            # Check if the specific file exists
            source_file = parts_dir / f"{file_name}.json"
            if not source_file.exists():
                results["errors"].append(f"Source file not found: {source_file}")
                return results
            
            # Step 2: Translate single file
            logger.info(f"🌐 Step 2: Translating {file_name}.json...")
            translation_success = translate_single_json_file(self.language, file_name)
            if not translation_success:
                results["errors"].append(f"Failed to translate {file_name}")
                return results
            results["steps"]["translation"] = {"success": True}
            logger.info(f"✅ Step 2 complete: {file_name} translated")


            # Step 3: Merge to final Excel
            logger.info("📊 Step 3: Merging to final Excel...")
            merge_success = merge_json_files_to_xlsx(self.language)
            if not merge_success:
                results["errors"].append("Failed to merge JSON files")
                return results
            results["steps"]["merging"] = {"success": True}
            logger.info("✅ Step 3 complete: Final Excel created")

            results["success"] = True
            logger.info(f"🎉 Single file pipeline completed for {file_name}")
            
        except Exception as e:
            error_msg = f"Single file pipeline error: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    def get_pipeline_status(self) -> Dict:
        """Get comprehensive status of the translation pipeline."""
        try:
            status = {
                "language": self.language,
                "excel_source": {},
                "json_parts": {},
                "translation_status": {},
                "merge_status": {},
                "overall_status": "unknown"
            }
            
            # Check Excel source
            excel_file = Path("source/Output_Final.xlsx")
            status["excel_source"] = {
                "exists": excel_file.exists(),
                "path": str(excel_file)
            }
            
            # Check JSON parts
            parts_dir = Path("parts") / self.language
            if parts_dir.exists():
                json_files = list(parts_dir.glob("*.json"))
                status["json_parts"] = {
                    "exists": True,
                    "count": len(json_files),
                    "files": [f.name for f in json_files]
                }
            else:
                status["json_parts"] = {"exists": False, "count": 0, "files": []}
            
            # Check translation status
            status["translation_status"] = get_translation_status(self.language)
            
            # Check merge status
            status["merge_status"] = get_merge_status(self.language)
            
            # Determine overall status
            if (status["excel_source"]["exists"] and 
                status["json_parts"]["exists"] and 
                status["translation_status"].get("total_translated", 0) > 0):
                if status["merge_status"].get("final_xlsx_exists", False):
                    status["overall_status"] = "complete"
                else:
                    status["overall_status"] = "translated_ready_to_merge"
            elif status["excel_source"]["exists"] and status["json_parts"]["exists"]:
                status["overall_status"] = "parts_ready_to_translate"
            elif status["excel_source"]["exists"]:
                status["overall_status"] = "ready_to_convert"
            else:
                status["overall_status"] = "no_source"
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting pipeline status: {str(e)}")
            return {"error": str(e)}

def print_pipeline_status(status: Dict):
    """Print pipeline status in a user-friendly format."""
    print(f"\n📊 Pipeline Status for {status['language']}")
    print("=" * 50)
    
    # Overall status
    status_icons = {
        "complete": "✅",
        "translated_ready_to_merge": "🔄",
        "parts_ready_to_translate": "📋",
        "ready_to_convert": "📁",
        "no_source": "❌",
        "unknown": "❓"
    }
    
    overall_status = status.get("overall_status", "unknown")
    icon = status_icons.get(overall_status, "❓")
    print(f"Overall Status: {icon} {overall_status.replace('_', ' ').title()}")
    
    # Excel source
    excel = status.get("excel_source", {})
    if excel.get("exists"):
        print(f"📁 Excel Source: ✅ {excel.get('path', 'Unknown')}")
    else:
        print("📁 Excel Source: ❌ Not found")
    
    # JSON parts
    parts = status.get("json_parts", {})
    if parts.get("exists"):
        print(f"📋 JSON Parts: ✅ {parts.get('count', 0)} files")
        for file_name in parts.get("files", [])[:5]:  # Show first 5 files
            print(f"   - {file_name}")
        if len(parts.get("files", [])) > 5:
            print(f"   ... and {len(parts.get('files', [])) - 5} more")
    else:
        print("📋 JSON Parts: ❌ Not found")
    
    # Translation status
    trans = status.get("translation_status", {})
    if "error" not in trans:
        print(f"🌐 Translation: {trans.get('total_translated', 0)}/{trans.get('total_source', 0)} files")
        if trans.get("pending_files"):
            print(f"   Pending: {', '.join(trans.get('pending_files', [])[:3])}")
            if len(trans.get("pending_files", [])) > 3:
                print(f"   ... and {len(trans.get('pending_files', [])) - 3} more")
    else:
        print(f"🌐 Translation: ❌ Error - {trans.get('error')}")
    
    # Merge status
    merge = status.get("merge_status", {})
    if "error" not in merge:
        if merge.get("final_xlsx_exists"):
            print("📊 Final Excel: ✅ Created")
        else:
            print("📊 Final Excel: ❌ Not created")
    else:
        print(f"📊 Final Excel: ❌ Error - {merge.get('error')}")

def main():
    """Main entry point for the translation pipeline."""
    parser = argparse.ArgumentParser(description="AI Excel Translation Pipeline")
    parser.add_argument("--language", "-l", default="japanese", 
                       help="Target language (default: japanese)")
    parser.add_argument("--items-per-part", "-i", type=int, default=200,
                       help="Items per JSON part (default: 200)")
    parser.add_argument("--file", "-f", 
                       help="Translate single file (without extension)")
    parser.add_argument("--status", "-s", default=False, action="store_true",
                       help="Show pipeline status only")
    parser.add_argument("--convert-to-json", "-c", default=False,
                       help="Convert Excel to JSON parts")
    parser.add_argument("--full", action="store_true",
                       help="Run full pipeline (Excel → JSON → Translate → Merge)")
    
    args = parser.parse_args()
    
    try:
        # Check environment
        if not os.getenv("GEMINI_API_KEY"):
            print("❌ ERROR: GEMINI_API_KEY not found in .env file")
            print("Please create a .env file with your Gemini API key")
            sys.exit(1)
        
        # Initialize pipeline
        pipeline = TranslationPipeline(args.language, args.items_per_part)
        
        # Show status only
        if args.status:
            status = pipeline.get_pipeline_status()
            print_pipeline_status(status)
            return
        
        # Run pipeline
        if args.file:
            # Single file translation
            print(f"🎯 Running single file translation for {args.file}")
            results = pipeline.run_single_file_pipeline(args.file, args.convert_to_json)
        elif args.full:
            # Full pipeline
            print(f"🚀 Running full translation pipeline")
            results = pipeline.run_full_pipeline(args.clean)
        else:
            # Default: show status and ask what to do
            status = pipeline.get_pipeline_status()
            print_pipeline_status(status)
            
            if status.get("overall_status") == "no_source":
                print("\n❌ No Excel source found. Please place Output_Final.xlsx in the source/ folder.")
                return
            
            if status.get("overall_status") == "ready_to_convert":
                print("\n🔄 Ready to convert Excel to JSON parts. Run with --full to start.")
                return
            
            if status.get("overall_status") == "parts_ready_to_translate":
                print("\n🔄 Ready to translate JSON parts. Run with --full to continue.")
                return
            
            if status.get("overall_status") == "translated_ready_to_merge":
                print("\n🔄 Ready to merge translated files. Run with --full to continue.")
                return
            
            if status.get("overall_status") == "complete":
                print("\n✅ Pipeline complete! Final Excel file created.")
                return
        
        # Show results
        if results.get("success"):
            print(f"\n🎉 Pipeline completed successfully!")
            if results.get("pipeline") == "single_file":
                print(f"File {results['file_name']} has been translated.")
            else:
                print(f"Full pipeline completed for {results['language']}.")
        else:
            print(f"\n❌ Pipeline failed with errors:")
            for error in results.get("errors", []):
                print(f"   - {error}")
            
            # Show status after failure
            print("\n📊 Current pipeline status:")
            status = pipeline.get_pipeline_status()
            print_pipeline_status(status)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
