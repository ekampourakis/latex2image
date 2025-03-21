# LaTeX2Image

A Python command-line tool for converting LaTeX math equations and pseudocode to PNG, JPG, or SVG images.

## Overview

This tool allows you to convert LaTeX math equations and pseudocode algorithms from JSON files to images. It uses a VS Code devcontainer with LaTeX environment to render with high quality and save them in your preferred format.

## Features

- Convert multiple LaTeX equations or pseudocode blocks in a single run
- Support for PNG, JPG, and SVG output formats
- Customizable scale options
- JSON-based input for batch processing
- Isolated VS Code devcontainer environment
- Support for algorithm and pseudocode environments

## Requirements

- VS Code with Dev Containers extension installed
- Docker Desktop
- Git

## Getting Started with Dev Containers

This project uses VS Code Dev Containers to provide a consistent environment with all dependencies pre-installed.

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Install [VS Code](https://code.visualstudio.com/)
3. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code
4. Clone this repository
5. Open the project in VS Code
6. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Dev Containers: Reopen in Container"

VS Code will build the container and set up the environment automatically. This may take a few minutes the first time.

## Adding Content to JSON Files

### Math Equations

The `equations.json` file contains the LaTeX equations you want to convert. You can edit this file directly in VS Code after opening the project in the dev container.

Each equation can be:

1. A simple string with the LaTeX expression:
   ```json
   "\\frac{a}{b}"
   ```

2. An object with additional properties:
   ```json
   {
     "id": "my_equation",
     "latex": "E = mc^2",
     "auto_align": true
   }
   ```

To add a new equation, just add a new entry to the `equations` array. For example:

```json
{
  "equations": [
    // ...existing equations...
    {
      "id": "my_new_equation",
      "latex": "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}"
    },
    // Or simply:
    "y = mx + b"
  ]
}
```

### Pseudocode Algorithms

The `pseudocode.json` file contains the LaTeX pseudocode algorithms you want to convert. Each algorithm should be defined using the `algorithm` and `algorithmic` environments.

Each pseudocode entry can be:

1. A simple string with the LaTeX pseudocode:
   ```json
   "\\begin{algorithm}\n\\caption{My Algorithm}\n\\begin{algorithmic}[1]\n\\State Do something\n\\end{algorithmic}\n\\end{algorithm}"
   ```

2. An object with additional properties:
   ```json
   {
     "id": "my_algorithm",
     "latex": "\\begin{algorithm}\n\\caption{My Algorithm}\n\\begin{algorithmic}[1]\n\\State Do something\n\\end{algorithmic}\n\\end{algorithm}",
     "auto_align": true
   }
   ```

To add a new pseudocode algorithm, add a new entry to the `pseudocode` array:
```json
{
  "pseudocode": [
    // ...existing pseudocode...
    {
      "id": "my_new_algorithm",
      "latex": "\\begin{algorithm}\n\\caption{New Algorithm}\n\\begin{algorithmic}[1]\n\\State Initialize variables\n\\While{condition}\n    \\State Do something\n\\EndWhile\n\\end{algorithmic}\n\\end{algorithm}"
    }
  ]
}
```

## Usage

Once the Dev Container is running, you can use the tool directly from the VS Code terminal:

### For Equations:

```bash
python latex2image.py equations.json
```

### For Pseudocode:

```bash
python latex2image.py pseudocode.json
```

### Command-line arguments:

```
python latex2image.py <input_json_file> --format png --scale 125% --output-dir output
```

- `<input_json_file>`: Path to the JSON file containing LaTeX equations or pseudocode
- `--format`: Output image format (choices: png, jpg, svg; default: png)
- `--scale`: Scale factor (default: 125%)
- `--output-dir`: Output directory (default: output)

## Examples

### Converting to different formats:

```bash
python latex2image.py equations.json --format svg
python latex2image.py pseudocode.json --format jpg
```

### Changing the scale:

```bash
python latex2image.py equations.json --scale 200%
```

### Using a custom output directory:

```bash
python latex2image.py pseudocode.json --output-dir my_algorithms
```

## JSON Format

### Equations JSON Format

The input JSON file for equations should contain an array of LaTeX equations under the `equations` key:

```json
{
  "equations": [
    {
      "id": "equation1",
      "latex": "E = mc^2",
      "auto_align": true
    },
    {
      "id": "equation2",
      "latex": "\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}"
    },
    "\\frac{a}{b}"
  ]
}
```

### Pseudocode JSON Format

The input JSON file for pseudocode should contain an array of LaTeX pseudocode algorithms under the `pseudocode` key:

```json
{
  "pseudocode": [
    {
      "id": "algorithm1",
      "latex": "\\begin{algorithm}\n\\caption{My Algorithm}\n\\begin{algorithmic}[1]\n\\State Initialize variables\n\\While{condition}\n    \\State Do something\n\\EndWhile\n\\end{algorithmic}\n\\end{algorithm}",
      "auto_align": true
    },
    "\\begin{algorithm}\\caption{Simple Algorithm}\\begin{algorithmic}[1]\\State Do something\\end{algorithmic}\\end{algorithm}"
  ]
}
```

Each item (equation or pseudocode) can be:

1. A string containing the LaTeX expression or algorithm
2. An object with the following properties:
   - `latex` (required): The LaTeX math expression or algorithm
   - `id` (optional): A unique identifier (used in filename)
   - `auto_align` (optional): Whether to wrap the equation in `align*` environment (default: true, only applies to equations)

## License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

## Acknowledgments

This tool is inspired by the [LaTeX2Image](https://github.com/joeraut/latex2image-web) web application by Joseph Rautenbach.
