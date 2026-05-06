# SUMMARY OF MODERN LIBRARIES AND METHODS:
# 1. pathlib.Path: Used for all filesystem operations instead of os.path. It provides an object-oriented API for path manipulation, directory creation (mkdir with parents=True, exist_ok=True), and file globbing (rglob).
# 2. argparse: Used for robust CLI argument parsing. Standard add_argument with action='store_true' is used for flags like --overwrite and --preserve-structure to ensure compatibility and avoid deprecated BooleanOptionalAction parameters.
# 3. Type Hinting: Used modern built-in types (e.g., list, dict, pathlib.Path) instead of typing module imports where applicable (PEP 585).
# 4. Error Handling: Specific exceptions (PermissionError, UnicodeDecodeError) are caught to provide granular feedback without crashing the batch process.

import argparse
import sys
import re
import os
from pathlib import Path

def _get_lang_from_ext(ext: str) -> str:
    extension_map = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript', 
        '.jsx': 'jsx', '.tsx': 'tsx', '.html': 'html', '.css': 'css', 
        '.json': 'json', '.md': 'markdown', '.yml': 'yaml', '.yaml': 'yaml',
        '.sh': 'bash', '.go': 'go', '.rs': 'rust', '.java': 'java', 
        '.cpp': 'cpp', '.c': 'c', '.h': 'c', '.cs': 'csharp', 
        '.rb': 'ruby', '.php': 'php', '.sql': 'sql', '.xml': 'xml'
    }
    return extension_map.get(ext.lower(), '')

def convert_text_to_markdown(text: str, title: str) -> str:
    """
    Parses codebase-convert output and formats it as a neat codeblock Markdown structure.
    
    Args:
        text (str): The raw text content.
        title (str): The filename to be used in the header.
        
    Returns:
        str: The formatted Markdown content.
    """
    # Check if it has ai-optimized markup tags or codebase-convert standard text headers
    folder_struct_match = re.search(r'(?:<folder_structure>|Folder Structure\n-+\n)([\s\S]*?)(?:</folder_structure>|\n\nFile Contents)', text)
    file_matches = list(re.finditer(r'<file path="([^"]+)">\n?([\s\S]*?)\n?</file>', text))
    
    if folder_struct_match and file_matches:
        folder_struct = folder_struct_match.group(1).strip('\n')
        md_output = f"# Folder Structure\n\n```text\n{folder_struct}\n```\n\n# File Contents\n"
        
        for match in file_matches:
            file_path = match.group(1)
            content = match.group(2).strip('\n')
            ext = os.path.splitext(file_path)[1]
            lang = _get_lang_from_ext(ext)
            md_output += f"\n### File: `{file_path}`\n\n```{lang}\n{content}\n```\n"
            
        return md_output

    # Fallback: Format the file with a header and empty codeblock (no language specifier for .txt files)
    return f"\n### File: `{title}`\n\n```\n{text}\n```\n"

def process_file(
    input_path: Path, 
    output_dir: Path, 
    base_input_dir: Path, 
    overwrite: bool, 
    preserve_structure: bool
) -> bool:
    """
    Processes a single text file, converting it to Markdown and saving it to the output directory.
    
    Args:
        input_path (Path): Path to the input .txt file.
        output_dir (Path): Path to the base output directory.
        base_input_dir (Path): Path to the base input directory (used for relative path calculation).
        overwrite (bool): Whether to overwrite existing files.
        preserve_structure (bool): Whether to mirror the input directory structure.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Determine the output path
        if preserve_structure:
            rel_path = input_path.relative_to(base_input_dir)
            output_path = output_dir / rel_path.with_suffix('.md')
        else:
            output_path = output_dir / input_path.with_suffix('.md').name
            
        # Check for existing file
        if output_path.exists() and not overwrite:
            print(f"[-] Skipped (already exists): {input_path.name}")
            return False
            
        # Read content with UTF-8 encoding
        try:
            content = input_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            print(f"[!] Error (encoding): {input_path} is not valid UTF-8.")
            return False
            
        # Check for empty files
        if not content.strip():
            print(f"[!] Warning (empty file): {input_path}")
            return False
            
        # Format as Markdown
        # Use relative path if preserving structure, else use the filename
        title_path = str(input_path.relative_to(base_input_dir)) if preserve_structure else input_path.name
        md_content = convert_text_to_markdown(content, title_path)
        
        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the Markdown file
        output_path.write_text(md_content, encoding='utf-8')
        print(f"[+] Converted: {input_path.name} -> {output_path}")
        return True
        
    except PermissionError:
        print(f"[!] Error (permission denied): {input_path}")
        return False
    except Exception as e:
        print(f"[!] Error (unexpected): {input_path} - {e}")
        return False

def main() -> None:
    """
    Main entry point for the CLI script.
    """
    parser = argparse.ArgumentParser(
        description="Batch convert plain text (.txt) files to Markdown (.md) files."
    )
    parser.add_argument(
        "input_dir", 
        type=Path, 
        help="Path to the input directory containing .txt files."
    )
    parser.add_argument(
        "output_dir", 
        type=Path, 
        help="Path to the output directory."
    )
    parser.add_argument(
        "--overwrite", 
        action="store_true", 
        help="Overwrite existing .md files in the output directory."
    )
    parser.add_argument(
        "--preserve-structure", 
        action="store_true", 
        help="Preserve the original directory structure in the output folder."
    )
    
    args = parser.parse_args()
    
    input_dir: Path = args.input_dir
    output_dir: Path = args.output_dir
    
    # Validate input directory
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"[!] Critical Error: Input directory '{input_dir}' does not exist or is not a directory.")
        sys.exit(1)
        
    # Find all .txt files recursively
    txt_files = list(input_dir.rglob("*.txt"))
    
    if not txt_files:
        print(f"[*] No .txt files found in '{input_dir}'. Exiting.")
        sys.exit(0)
        
    print(f"[*] Found {len(txt_files)} .txt file(s). Starting conversion...")
    
    success_count = 0
    for txt_file in txt_files:
        # Skip directories that might end in .txt (edge case)
        if not txt_file.is_file():
            continue
            
        success = process_file(
            input_path=txt_file,
            output_dir=output_dir,
            base_input_dir=input_dir,
            overwrite=args.overwrite,
            preserve_structure=args.preserve_structure
        )
        if success:
            success_count += 1
            
    print(f"[*] Conversion complete. Successfully converted {success_count}/{len(txt_files)} files.")

if __name__ == "__main__":
    main()