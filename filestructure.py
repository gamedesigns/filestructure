import os
import argparse

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")
    except OSError as e:
        print(f"Error creating directory {path}: {e}")

def create_file(path):
    try:
        with open(path, 'w') as file:
            pass  # Create an empty file
        print(f"Created file: {path}")
    except OSError as e:
        print(f"Error creating file {path}: {e}")

def parse_structure(text):
    structure = []
    current_path = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        leading_spaces = len(line) - len(line.lstrip(' '))
        depth = leading_spaces // 4
        name = line.lstrip(' ').lstrip('-').strip()
        is_dir = name.endswith('/')
        if is_dir:
            name = name[:-1]
        while len(current_path) > depth:
            current_path.pop()
        current_path.append(name)
        full_path = '/'.join(current_path)
        if is_dir:
            structure.append(('dir', full_path))
        else:
            structure.append(('file', full_path))
        if is_dir:
            current_path.append(name)
    return structure

def main():
    print("FileStructure Creator v1.0")
    print("This program creates a file and folder structure based on a description in a text file.")
    print()
    
    parser = argparse.ArgumentParser(description="Create project directory structure.")
    parser.add_argument("base_dir", nargs='?', default=os.path.dirname(os.path.abspath(__file__)), help="Base directory for the project.")
    parser.add_argument("--file", default="structure.txt", help="Path to the text file describing the structure.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()
    
    base_dir = args.base_dir
    file_path = args.file
    verbose = args.verbose
    
    try:
        with open(file_path, 'r') as file:
            text_structure = file.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return
    except IOError as e:
        print(f"Error: {e}")
        return
    
    structure = parse_structure(text_structure)
    
    # Build full paths
    full_structure = [(item_type, os.path.join(base_dir, path)) for item_type, path in structure]
    
    # Print the list of items to be created
    print("The following directories and files will be created:")
    for item_type, path in full_structure:
        print(f"- {path}")
    
    # Ask for user confirmation
    confirmation = input("Proceed? [y/N]: ")
    if confirmation.lower() not in ['y', 'yes']:
        print("Operation aborted.")
        return
    
    # Create directories and files
    for item_type, path in full_structure:
        if item_type == 'dir':
            create_directory(path)
        elif item_type == 'file':
            create_file(path)

if __name__ == "__main__":
    main()