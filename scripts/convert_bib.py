#!/usr/bin/env python3
import panflute as pf
import json
import sys
from pathlib import Path

def title_case(text):
    # List of words to keep lowercase
    small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'en', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'via', 'vs'}
    
    # Split the text into words
    words = text.split()
    
    result = []
    
    for i, word in enumerate(words):
        # Always capitalize first and last word
        if word[0].isupper():
            result.append(word)
        elif i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        # Check if word should be lowercase
        elif word.lower() in small_words:
            result.append(word.lower())
        # Capitalize word
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)

def convert_bib_to_json(input_file, output_file):
    try:
        # Run pandoc to convert BibTeX to JSON
        doc = pf.convert_text(
            Path(input_file).read_text(encoding='utf-8'),
            input_format='bibtex',
            output_format='csljson',
            standalone=True
        )
        
        # Parse the JSON
        entries = json.loads(doc)
        
        # Apply title case to titles
        for entry in entries:
            if 'title' in entry:
                entry['title'] = title_case(entry['title'])
        
        # Write the modified JSON to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
            
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
