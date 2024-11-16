#!/usr/bin/env python3
import panflute as pf
import json
import sys
from pathlib import Path

def convert_bib_to_json(input_file, output_file):
    try:
        # Run pandoc to convert BibTeX to JSON
        doc = pf.convert_text(
            Path(input_file).read_text(encoding='utf-8'),
            input_format='bibtex',
            output_format='csljson',
            standalone=True
        )
        
        # Write the output to the specified file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc)
            
        print(f"Successfully converted {input_file} to {output_file}")
        
    except Exception as e:
        print(f"Error converting file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_bib.py <input_bib_file> <output_json_file>", file=sys.stderr)
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
        
    convert_bib_to_json(input_file, output_file)

if __name__ == '__main__':
    main()
