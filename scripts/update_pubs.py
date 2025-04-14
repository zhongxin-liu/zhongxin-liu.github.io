#!/usr/bin/env python3
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

def load_csl_json(file_path):
    """Load and parse CSL JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_authors(authors):
    """Format author names from CSL JSON format."""
    formatted_authors = []
    for author in authors:
        if 'literal' in author:
            name = author['literal']
        else:
            name_parts = []
            if 'given' in author:
                name_parts.append(author['given'])
            if 'family' in author:
                name_parts.append(author['family'])
            name = ' '.join(name_parts)
        formatted_authors.append(name)
    
    # Bold my name in the author list
    my_name = ["Zhongxin Liu", "Zhongxin Liu*"]
    formatted_authors = [f"<u>{author}</u>" if author in my_name else author 
                        for author in formatted_authors]
    
    if len(formatted_authors) > 1:
        return f"{', '.join(formatted_authors[:-1])} and {formatted_authors[-1]}"
    return formatted_authors[0]

def bold_abbreviation(venue):
    """Bold the conference/journal abbreviation in parentheses."""
    pattern = r'\((.*?)\)'
    match = re.search(pattern, venue)
    if match:
        abbrev = match.group(1)
        return venue.replace(f"({abbrev})", f"(<b>{abbrev}</b>)")
    return venue

def format_venue(item):
    """Format publication venue with volume, issue, pages if available."""
    venue_parts = []
    
    # Container title (journal/conference name)
    if 'container-title' in item:
        venue = item['container-title']
        venue = bold_abbreviation(venue)
        venue_parts.append(venue)
    
    # Volume and issue
    # if 'volume' in item:
    #     volume_str = f"vol. {item['volume']}"
    #     if 'issue' in item:
    #         volume_str += f", no. {item['issue']}"
    #     venue_parts.append(volume_str)
    
    # Pages
    # if 'page' in item:
    #     venue_parts.append(f"pp. {item['page']}")

    if item['type'] != "paper-conference":
    # Year
        if 'issued' in item and 'date-parts' in item['issued']:
            year = item['issued']['date-parts'][0][0]
            venue_parts.append(str(year))
        
        if 'issue' in item and 'volume' in item:
            venue_parts.append(f"{item['volume']}({item['issue']})")  # Added the missing closing curly brace here
    
    return ', '.join(venue_parts)

def should_include_publication(item):
    """Check if a publication should be included in the output."""
    return True  # You can add filtering logic here if needed

def generate_publication_html(item):
    """Generate HTML for a single publication."""
    html = '<li>\n'
    
    # Title
    shorttitle = item.get('title-short', '')
    title = item.get('title', '')
    html += f'<b><span style="color: #0b5394;">[{shorttitle}]</span> {title}</b><br>\n'
    
    # Authors
    if 'author' in item:
        authors = format_authors(item['author'])
        html += f'{authors}<br>\n'
    
    # Venue and other details
    venue = format_venue(item)
    if venue:
        html += f'{venue}.\n'
    
    # Additional notes (e.g., acceptance status)
    if 'note' in item:
        if "award" in item["note"].lower():
            note = f'[<span class="red">{item["note"]}</span> 🏆]'
        else:
            note = f' {item["note"]}.'
        html += f'{note}\n'
    
    html += '<br>\n'
    
    # Add DOI and GitHub links
    links = []
    if 'DOI' in item:
        doi_url = f"https://doi.org/{item['DOI']}"
        links.append(f'<a href="{doi_url}" target="_blank" class="publication-link paper-link">Paper</a>')
    
    if 'URL' in item and 'github.com' in item['URL'].lower():
        links.append(f'<a href="{item["URL"]}" target="_blank" class="publication-link code-link">Code</a>')
    
    if links:
        html += ' '.join(links) + '<br>\n'
    
    html += '</li>\n'
    return html

def update_publications_section(html_content, publications):
    """Update the publications section in the HTML content."""
    new_content = '<div id="publications">\n'
    new_content += '<h2>Publications</h2>\n<ul>\n'
    
    # Use publications in their original order from pub2.json
    for item in publications:
        if "chinese" in item['id'].lower():
            continue
        if should_include_publication(item):
            new_content += generate_publication_html(item)
    
    new_content += '</ul>\n</div>\n'
    
    # Replace the existing publications section
    pattern = r'<div id="publications">.*?</div>\s*'
    replacement = new_content
    updated_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    return updated_html

def main():
    # File paths
    if len(sys.argv) != 3:
        print("Usage: python update_pubs.py <input_html_file> <output_json_file>", file=sys.stderr)
        sys.exit(1)
        
    html_path = Path(sys.argv[1])
    json_path = Path(sys.argv[2])
    
    if not json_path.exists():
        print(f"Error: JSON file '{json_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Load the CSL JSON data
    publications = load_csl_json(json_path)
    
    # Read the current HTML content
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update the publications section
    updated_html = update_publications_section(html_content, publications)
    
    # Create a backup of the original file
    backup_path = html_path.with_suffix('.html.bak')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Write the updated HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"Publications updated successfully!")
    print(f"Backup saved to: {backup_path}")

if __name__ == '__main__':
    main()
