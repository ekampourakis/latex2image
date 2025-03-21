#!/usr/bin/env python3
import os
import json
import shutil
import argparse
import subprocess
import uuid
from pathlib import Path
import time
from PIL import Image

class Latex2Image:
    def __init__(self, output_format='png', scale='1.25', output_dir='output'):
        """
        Initialize the Latex2Image converter.
        
        Args:
            output_format (str): The output image format (png, jpg, or svg)
            scale (str): The scale factor for the image
            output_dir (str): The directory to save the output images
        """
        self.temp_dir = 'temp'
        self.output_dir = output_dir
        self.output_format = output_format.lower()
        self.scale = self._parse_scale(scale)
        self.debug = True  # Enable debugging
        
        # Create temp and output directories if they don't exist
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Validate output format
        if self.output_format not in ['png', 'jpg', 'svg']:
            raise ValueError(f"Invalid output format: {output_format}. Must be png, jpg, or svg.")

    def _parse_scale(self, scale):
        """Convert scale from percentage to decimal format"""
        scale_map = {
            '10%': '0.1',
            '25%': '0.25',
            '50%': '0.5',
            '75%': '0.75',
            '100%': '1.0',
            '125%': '1.25',
            '150%': '1.5',
            '200%': '2.0',
            '500%': '5.0',
            '1000%': '10.0'
        }
        
        if scale in scale_map:
            return scale_map[scale]
        elif isinstance(scale, str) and scale.endswith('%'):
            try:
                return str(float(scale.strip('%')) / 100)
            except ValueError:
                return '1.25'  # Default
        return scale

    def get_latex_template(self, equation, is_pseudocode=False):
        """
        Generate the LaTeX document template.
        
        Args:
            equation (str): The LaTeX equation or pseudocode to include in the template
            is_pseudocode (bool): Whether this is pseudocode (requiring algorithm packages)
            
        Returns:
            str: The complete LaTeX document
        """
        # Base packages for all documents
        base_packages = r"""\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{xcolor}
\usepackage[utf8]{inputenc}
\usepackage{siunitx}
\thispagestyle{empty}
"""
        
        # Add algorithm packages only for pseudocode
        if is_pseudocode:
            # Don't include both algorithmic and algpseudocode as they conflict
            algorithm_packages = r"""\usepackage{algorithm}
\usepackage{algorithmicx}
\usepackage{algpseudocode}
\usepackage{graphicx}
\renewcommand{\thealgorithm}{}  % Remove algorithm numbering
\floatname{algorithm}{}         % Remove 'Algorithm' prefix
"""

            # Preprocess equation to adjust caption if needed
            if r'\begin{algorithm}' in equation and r'\caption{' in equation:
                # Extract the caption content
                import re
                caption_match = re.search(r'\\caption\{(.*?)\}', equation)
                if caption_match:
                    caption_text = caption_match.group(1)
                    # Replace original caption with "Algorithm: original_caption"
                    equation = equation.replace(f'\\caption{{{caption_text}}}', f'\\caption{{Algorithm: {caption_text}}}')
                
            return base_packages + algorithm_packages + r"\begin{document}" + "\n" + equation + "\n" + r"\end{document}"
        else:
            return base_packages + r"\begin{document}" + "\n" + equation + "\n" + r"\end{document}"

    def convert_equation(self, equation, eq_id=None, auto_align=True, is_pseudocode=False):
        """
        Convert a LaTeX equation or pseudocode to an image.
        
        Args:
            equation (str): The LaTeX equation or pseudocode
            eq_id (str, optional): A unique ID for this equation. If not provided,
                                   a random ID will be generated.
            auto_align (bool): Whether to wrap the equation in align* environment
            is_pseudocode (bool): Whether this is pseudocode
            
        Returns:
            str: The path to the output image file
        """
        if eq_id is None:
            eq_id = str(uuid.uuid4())[:8]
            
        # Create temp directory for this equation
        eq_temp_dir = os.path.join(self.temp_dir, eq_id)
        os.makedirs(eq_temp_dir, exist_ok=True)
        
        # Wrap equation in align* environment if requested and if it's not already in an environment
        if auto_align and not is_pseudocode and not (r'\begin{' in equation or r'\end{' in equation):
            equation = r'\begin{align*}' + equation + r'\end{align*}'
            
        # Write the .tex file
        tex_file = os.path.join(eq_temp_dir, 'equation.tex')
        with open(tex_file, 'w') as f:
            f.write(self.get_latex_template(equation, is_pseudocode))
            
        # In debug mode, save a copy of the tex file to inspect
        if self.debug:
            debug_dir = os.path.join(self.temp_dir, 'debug')
            os.makedirs(debug_dir, exist_ok=True)
            shutil.copy(tex_file, os.path.join(debug_dir, f'{eq_id}.tex'))
            
        # Run LaTeX commands directly
        try:
            # Run latex with more verbose output
            latex_log_file = os.path.join(eq_temp_dir, 'latex_output.log')
            with open(latex_log_file, 'w') as log_file:
                latex_process = subprocess.run(
                    ['latex', '-no-shell-escape', '-interaction=nonstopmode', 'equation.tex'],
                    cwd=eq_temp_dir,
                    check=False,
                    timeout=30,
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
            
            # If there was an error, copy the log file to debug directory
            if latex_process.returncode != 0:
                if self.debug:
                    shutil.copy(latex_log_file, os.path.join(debug_dir, f'{eq_id}_error.log'))
                    print(f"Error compiling LaTeX for {eq_id}. Log saved to {os.path.join(debug_dir, f'{eq_id}_error.log')}")
                else:
                    with open(latex_log_file, 'r') as log_file:
                        print(f"Error compiling LaTeX for {eq_id}: {log_file.read()[-500:]}")  # Show last 500 chars
                shutil.rmtree(eq_temp_dir, ignore_errors=True)
                return None
            
            # Check if the DVI file was created
            dvi_file = os.path.join(eq_temp_dir, 'equation.dvi')
            if not os.path.exists(dvi_file):
                print(f"DVI file not created for {eq_id}")
                shutil.rmtree(eq_temp_dir, ignore_errors=True)
                return None
                
            # Convert .dvi to .svg file
            dvisvgm_log_file = os.path.join(eq_temp_dir, 'dvisvgm_output.log')
            with open(dvisvgm_log_file, 'w') as log_file:
                dvisvgm_process = subprocess.run(
                    ['dvisvgm', '--no-fonts', f'--scale={self.scale}', '--exact', 'equation.dvi'],
                    cwd=eq_temp_dir,
                    check=False,
                    timeout=20,
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
            
            if dvisvgm_process.returncode != 0:
                if self.debug:
                    shutil.copy(dvisvgm_log_file, os.path.join(debug_dir, f'{eq_id}_dvisvgm_error.log'))
                    print(f"Error converting DVI to SVG for {eq_id}. Log saved to {os.path.join(debug_dir, f'{eq_id}_dvisvgm_error.log')}")
                else:
                    with open(dvisvgm_log_file, 'r') as log_file:
                        print(f"Error converting DVI to SVG for {eq_id}: {log_file.read()}")
                shutil.rmtree(eq_temp_dir, ignore_errors=True)
                return None
            
        except subprocess.TimeoutExpired as e:
            print(f"Timeout while processing {eq_id}: {e}")
            shutil.rmtree(eq_temp_dir, ignore_errors=True)
            return None
        except Exception as e:
            print(f"Unexpected error processing {eq_id}: {e}")
            shutil.rmtree(eq_temp_dir, ignore_errors=True)
            return None
            
        # Source and destination paths
        svg_file = os.path.join(eq_temp_dir, 'equation.svg')
        if not os.path.exists(svg_file):
            print(f"SVG file not created for {eq_id}")
            shutil.rmtree(eq_temp_dir, ignore_errors=True)
            return None
            
        output_filename = f"img-{eq_id}.{self.output_format}"
        output_file = os.path.join(self.output_dir, output_filename)
        
        # Handle different output formats
        try:
            if self.output_format == 'svg':
                shutil.copy(svg_file, output_file)
            else:
                # Convert SVG to PNG/JPG
                if self.output_format == 'png':
                    self._convert_svg_to_png(svg_file, output_file)
                elif self.output_format == 'jpg':
                    self._convert_svg_to_jpg(svg_file, output_file)
        except Exception as e:
            print(f"Error converting output format: {e}")
            shutil.rmtree(eq_temp_dir, ignore_errors=True)
            return None
            
        # In debug mode, keep the temp files, otherwise clean up
        if not self.debug:
            shutil.rmtree(eq_temp_dir, ignore_errors=True)
        
        print(f"Successfully created {output_file}")
        return output_file
        
    def _convert_svg_to_png(self, svg_file, png_file):
        """
        Convert SVG to PNG using cairosvg.
        
        Args:
            svg_file (str): Path to the SVG file
            png_file (str): Path to the output PNG file
        """
        import cairosvg
        cairosvg.svg2png(url=svg_file, write_to=png_file)
    
    def _convert_svg_to_jpg(self, svg_file, jpg_file):
        """
        Convert SVG to JPG using a two-step process:
        1. Convert SVG to PNG
        2. Convert PNG to JPG with white background
        
        Args:
            svg_file (str): Path to the SVG file
            jpg_file (str): Path to the output JPG file
        """
        # Create a temporary PNG file
        temp_png = jpg_file.replace('.jpg', '.temp.png')
        self._convert_svg_to_png(svg_file, temp_png)
        
        # Convert PNG to JPG with white background
        try:
            img = Image.open(temp_png)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new(img.mode[:-1], img.size, (255, 255, 255))
                background.paste(img, img.split()[-1])
                img = background
            img.convert('RGB').save(jpg_file, 'JPEG', quality=95)
            img.close()
            
            # Remove temporary PNG file
            os.remove(temp_png)
        except Exception as e:
            raise Exception(f"Error converting PNG to JPG: {e}")
            
    def process_json_file(self, json_file):
        """
        Process a JSON file containing LaTeX equations or pseudocode.
        
        Args:
            json_file (str): Path to the JSON file
            
        Returns:
            list: A list of output image paths
        """
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        # Check for equations or pseudocode array
        items = []
        is_pseudocode = False
        if 'equations' in data:
            items = data.get('equations', [])
            item_type = "equation"
        elif 'pseudocode' in data:
            items = data.get('pseudocode', [])
            item_type = "pseudocode"
            is_pseudocode = True
        else:
            raise ValueError("No equations or pseudocode found in the JSON file")
            
        if not items:
            raise ValueError(f"No {item_type}s found in the JSON file")
            
        output_files = []
        for i, item_data in enumerate(items):
            if isinstance(item_data, str):
                # Simple string format
                content = item_data
                item_id = f"{item_type}{i}"
                auto_align = True
            else:
                # Object format
                content = item_data.get('latex')
                if not content:
                    print(f"Skipping {item_type} at index {i}: No 'latex' field found")
                    continue
                    
                item_id = item_data.get('id', f"{item_type}{i}")
                auto_align = item_data.get('auto_align', True)
                
            print(f"Processing {item_type} {i+1}/{len(items)}: {item_id}")
            output_file = self.convert_equation(content, item_id, auto_align, is_pseudocode)
            if output_file:
                output_files.append(output_file)
                
        return output_files

def main():
    parser = argparse.ArgumentParser(description='Convert LaTeX equations and pseudocode to images')
    parser.add_argument('json_file', help='Path to the JSON file containing LaTeX equations or pseudocode')
    parser.add_argument('--format', choices=['png', 'jpg', 'svg'], default='png',
                        help='Output image format (default: png)')
    parser.add_argument('--scale', default='125%',
                        help='Scale factor (default: 125%)')
    parser.add_argument('--output-dir', default='output',
                        help='Output directory (default: output)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (keeps temporary files)')
    
    args = parser.parse_args()
    
    try:
        converter = Latex2Image(
            output_format=args.format,
            scale=args.scale,
            output_dir=args.output_dir
        )
        
        if args.debug:
            converter.debug = True
            
        start_time = time.time()
        output_files = converter.process_json_file(args.json_file)
        elapsed_time = time.time() - start_time
        
        print(f"\nProcessed {len(output_files)} items in {elapsed_time:.2f} seconds")
        print(f"Output files saved to {os.path.abspath(args.output_dir)}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == '__main__':
    main()