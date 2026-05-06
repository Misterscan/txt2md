# txt2md

A CLI tool to batch convert plain text (`.txt`) files to Markdown (`.md`). It understands the output format of [codebase-convert](https://github.com/Misterscan/codebase_convert) and formats code blocks with proper syntax highlighting based on file extensions.

## Features

- Recursively finds all `.txt` files in an input directory
- Parses `codebase-convert` output (both XML-tagged and standard formats) into clean, syntax-highlighted Markdown
- Falls back to a plain code block for generic text files
- Optional directory structure preservation in the output
- Skips existing files unless `--overwrite` is specified
- Handles encoding errors and empty files gracefully

## Requirements

- Python 3.9+

## Usage

```bash
python main.py <input_dir> <output_dir> [--overwrite] [--preserve-structure]
```

### Arguments

| Argument | Description |
|---|---|
| `input_dir` | Path to the directory containing `.txt` files |
| `output_dir` | Path to the directory where `.md` files will be saved |
| `--overwrite` | Overwrite existing `.md` files in the output directory |
| `--preserve-structure` | Mirror the input directory structure in the output folder |

### Examples

Convert all `.txt` files from `input/` to `output/`:
```bash
python main.py input/ output/
```

Convert and overwrite any existing files:
```bash
python main.py input/ output/ --overwrite
```

Convert while preserving the folder structure:
```bash
python main.py input/ output/ --preserve-structure
```

## Output Format

### codebase-convert files

If a `.txt` file contains `codebase-convert` output (XML tags or standard headers), it is formatted as:

```markdown
# Folder Structure

\`\`\`text
...
\`\`\`

# File Contents

### File: `src/main.py`

\`\`\`python
...
\`\`\`
```

### Generic text files

All other `.txt` files are wrapped in a plain code block:

```markdown
### File: `filename.txt`

\`\`\`
...
\`\`\`
```
