# CodeMerger

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CodeMerger is a desktop application that helps analyze and export the file structure and content of your project. It was created to simplify code sharing with AI assistants, providing a clean, organized representation of your codebase.

![CodeMerger Screenshot](screenshot.png)

## Features

- **Project Structure Analysis**: Scan any folder to analyze its file structure
- **Content Extraction**: Extract and display the content of text files
- **Smart Binary Detection**: Automatically detect and skip binary files
- **Customizable Limits**: Set maximum file size and content length limitations
- **File Filtering**: Filter files by status (OK, ERROR, BINARY, etc.)
- **Search Capabilities**: Search by filename or file content
- **Export Options**: Export your project in Markdown or JSON format
- **Ignore Patterns**: Set patterns to ignore certain files or directories
- **Multi-threaded Processing**: Fast scanning with parallel processing

## Why CodeMerger?

When working with AI assistants like ChatGPT, Claude, or GitHub Copilot, sharing project structure and code is essential for getting accurate help. CodeMerger simplifies this process by:

1. Creating a clean, organized representation of your codebase
2. Filtering out binary files and large files that aren't relevant
3. Providing content in an easily shareable format (Markdown or JSON)
4. Giving you control over what information is included

## Installation

### Prerequisites

- Python 3.6 or higher
- Required packages: tkinter, charset-normalizer, binaryornot

### Setup

1. Clone this repository or download the source code

```bash
git clone https://github.com/yourusername/codemerger.git
cd codemerger
```

2. Install the required dependencies

```bash
pip install charset-normalizer binaryornot
```

3. Run the application

```bash
python manager.py
```

## Usage

1. **Select Folder**: Click the "Select" button to choose the folder you want to analyze
2. **Start Scanning**: Click the "Start" button to begin scanning the selected folder
3. **View Results**: Browse the file list to see all files in the project
4. **Filter Files**: Use the dropdown menu to filter files by status
5. **Search**: Use the search fields to find files by name or content
6. **View Content**: Double-click on a file to view its content
7. **Export**: Click "Export MD" or "Export JSON" to save the project structure and content

## Configuration

CodeMerger can be configured through the user interface or by editing the `codemerger_config.json` file:

- **Maximum Content Length**: Limit the number of characters to extract from each file
- **Maximum File Size**: Skip files that exceed the specified size (in KB)
- **Excluded Files**: List of filenames to exclude from content extraction
- **Ignore Patterns**: Patterns to ignore when scanning (e.g., `*.log`, `node_modules/*`)

## Export Formats

### Markdown

Markdown export includes:
- Project summary with file count
- Folder structure
- File details (extension, size, encoding)
- File content with syntax highlighting

### JSON

JSON export includes:
- Project metadata
- Complete folder structure
- File details and content
- File status and error information

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Keywords and Tags

#project-structure-analyzer #code-sharing #ai-assistant-tool #file-parser #project-exporter #markdown-generator #json-generator #codebase-analyzer #development-tool #code-documentation #project-visualization #file-content-extractor #binary-file-detector #project-scanner #code-organization #ai-collaboration-tool #code-summarizer #project-explorer #file-structure-analyzer #code-sharing-tool