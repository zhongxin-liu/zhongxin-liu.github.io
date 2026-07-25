#!/usr/bin/env python3
import panflute as pf
import json
import sys
from pathlib import Path
from generate_cv_publications import parse_bibtex


def bibtex_title_text(text):
    """Return the display text while preserving BibTeX title capitalization."""
    return text.replace('{', '').replace('}', '')

def title_case(text):
    # List of words to keep lowercase
    small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'en', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'via', 'vs'}
    
    # Split the text into words
    words = text.split()
    
    result = []
    
    for i, word in enumerate(words):
        # Preserve intentional mixed-case words such as iCoRe or ReCode.
        if any(ch.isupper() for ch in word[1:]) and any(ch.islower() for ch in word):
            result.append(word)
        # Always capitalize first and last word
        elif word[0].isupper():
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
        bibtex = Path(input_file).read_text(encoding='utf-8')
        source_titles = {
            entry.key: bibtex_title_text(entry.fields['title'])
            for entry in parse_bibtex(bibtex)
            if 'title' in entry.fields
        }

        # Run pandoc to convert BibTeX to JSON
        doc = pf.convert_text(
            bibtex,
            input_format='bibtex',
            output_format='csljson',
            standalone=True
        )
        
        # Parse the JSON
        entries = json.loads(doc)
        
        # Preserve source title capitalization and normalize other display fields.
        for entry in entries:
            if 'title' in entry:
                entry['title'] = source_titles.get(
                    entry.get('id'), title_case(entry['title'])
                )
            if 'container-title' in entry:
                container_title = title_case(entry['container-title'])
                if ' (' in container_title:
                    title, short = container_title.split(' (')
                    short = short.upper()
                    if short.endswith("FINDINGS)"):
                        short = short.replace("FINDINGS", "Findings")
                    if short.startswith("NEURIPS"):
                        short = short.replace("NEURIPS", "NeurIPS")
                    container_title = ' ('.join([title, short])
                entry['container-title'] = container_title
            if 'title-short' in entry:
                entry['title-short'] = title_case(entry['title-short'])
        
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
