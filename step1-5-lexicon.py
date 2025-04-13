import os
import json
import re

# Configuration - Hard-coded values
DIRECTORY_TO_PROCESS = "data/OrigData"  # Change this to your directory path
LEXICON_PATH = "lexicon.json"  # Path to your lexicon file

def load_lexicon(lexicon_path):
    """Load the lexicon file containing word replacements."""
    try:
        with open(lexicon_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Lexicon file '{lexicon_path}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Lexicon file '{lexicon_path}' is not valid JSON.")
        exit(1)

def replace_words_in_text(text, lexicon):
    """Replace whole words in text according to the lexicon (case-insensitive). 
    Return the modified text and a list of replacements made."""
    if not isinstance(text, str):
        return text, []
    
    replacements_made = []
    
    # Create a dictionary mapping lowercase words to their replacements
    # This is to handle case-insensitive matching
    case_insensitive_lexicon = {k.lower(): v for k, v in lexicon.items()}
    
    # Create a pattern that matches whole words only (case-insensitive)
    pattern = r'\b(?:' + '|'.join(re.escape(word) for word in case_insensitive_lexicon.keys()) + r')\b'
    
    def replace_match(match):
        original = match.group(0)
        replacement = case_insensitive_lexicon[original.lower()]
        replacements_made.append((original, replacement))
        return replacement
    
    # Use re.IGNORECASE flag for case-insensitive matching
    modified_text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    return modified_text, replacements_made

def process_json_file(filepath, lexicon):
    """Process a JSON file, replacing words in the 'sentence' field."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        modified = False
        all_replacements = []
        
        # If data is a dictionary and has a 'sentence' key
        if isinstance(data, dict):
            if 'sentence' in data and isinstance(data['sentence'], str):
                original = data['sentence']
                data['sentence'], replacements = replace_words_in_text(data['sentence'], lexicon)
                all_replacements.extend(replacements)
                modified = original != data['sentence']
            # Process nested dictionaries and lists
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    data[key], sub_modified, sub_replacements = process_nested_json(value, lexicon)
                    all_replacements.extend(sub_replacements)
                    modified = modified or sub_modified
        
        # If data is a list, process each element
        elif isinstance(data, list):
            data, modified, nested_replacements = process_nested_json(data, lexicon)
            all_replacements.extend(nested_replacements)
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            return True, all_replacements
        return False, []
    
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error processing file {filepath}: {e}")
        return False, []

def process_nested_json(data, lexicon):
    """Process nested dictionaries and lists in JSON data."""
    modified = False
    all_replacements = []
    
    if isinstance(data, dict):
        if 'sentence' in data and isinstance(data['sentence'], str):
            original = data['sentence']
            data['sentence'], replacements = replace_words_in_text(data['sentence'], lexicon)
            all_replacements.extend(replacements)
            modified = original != data['sentence']
        
        for key, value in list(data.items()):
            if isinstance(value, (dict, list)):
                data[key], sub_modified, sub_replacements = process_nested_json(value, lexicon)
                all_replacements.extend(sub_replacements)
                modified = modified or sub_modified
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                data[i], sub_modified, sub_replacements = process_nested_json(item, lexicon)
                all_replacements.extend(sub_replacements)
                modified = modified or sub_modified
            elif isinstance(item, str) and 'sentence' in data and data.index(item) == data.index('sentence') + 1:
                # This assumes a pattern where 'sentence' might be a key in a list followed by its value
                original = item
                data[i], replacements = replace_words_in_text(item, lexicon)
                all_replacements.extend(replacements)
                modified = original != data[i]
    
    return data, modified, all_replacements

def process_directory(directory, lexicon):
    """Process all JSON files in the specified directory and its subdirectories."""
    modified_count = 0
    file_count = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.json') and file != os.path.basename(LEXICON_PATH):
                file_path = os.path.join(root, file)
                file_count += 1
                modified, replacements = process_json_file(file_path, lexicon)
                
                if modified:
                    modified_count += 1
                    print(f"\nModified: {file_path}")
                    
                    # Group replacements by original word for cleaner output
                    replacement_counts = {}
                    for orig, repl in replacements:
                        if (orig, repl) not in replacement_counts:
                            replacement_counts[(orig, repl)] = 1
                        else:
                            replacement_counts[(orig, repl)] += 1
                    
                    # Print the replacements made in this file
                    for (orig, repl), count in replacement_counts.items():
                        print(f"  - Replaced '{orig}' with '{repl}' ({count} times)")
    
    return file_count, modified_count

def main():
    print(f"Starting text replacement in JSON files (case-insensitive)...")
    print(f"Directory: {DIRECTORY_TO_PROCESS}")
    print(f"Lexicon file: {LEXICON_PATH}")
    
    lexicon = load_lexicon(LEXICON_PATH)
    print(f"Loaded lexicon with {len(lexicon)} entries.")
    
    total_files, modified_files = process_directory(DIRECTORY_TO_PROCESS, lexicon)
    
    print(f"\nSummary:")
    print(f"Processed {total_files} JSON files.")
    print(f"Modified {modified_files} files.")

if __name__ == '__main__':
    main()