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
        with open(path, 'w', encoding='utf-8') as file:
            pass  # Create an empty file
        print(f"Created file: {path}")
    except OSError as e:
        print(f"Error creating file {path}: {e}")

def parse_line(line):
    line = line.expandtabs()
    i = 0
    depth = 0
    while i < len(line):
        if line[i] == '│':
            if line[i:i+4] == '│   ':
                depth += 1
                i += 4
            else:
                i += 1
        elif line[i] in '├└':
            depth += 1
            if line[i:i+3] in ['├──', '└──']:
                i += 3
            else:
                i += 1
        else:
            break
    name = line[i:].strip()
    name = name.lstrip('├└─│ ')
    return depth, name

def parse_tree_lines(text):
    lines = text.strip().split('\n')
    for line in lines:
        depth, name = parse_line(line)
        yield depth, name

def parse_structure(text):
    structure = []
    stack = [('', 0)]  # (path, depth)
    for depth, name in parse_tree_lines(text):
        while stack and stack[-1][1] >= depth:
            stack.pop()
        parent_path = stack[-1][0] if stack else ''
        full_path = os.path.join(parent_path, name)
        is_dir = name.endswith('/')
        structure.append(('dir' if is_dir else 'file', full_path))
        if is_dir:
            stack.append((full_path, depth))
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
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            text_structure = file.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return
    except IOError as e:
        print(f"Error: {e}")
        return

    structure = parse_structure(text_structure)

    # Ensure the root directory is included
    root_dir = os.path.join(base_dir, 'loot_box_game')
    create_directory(root_dir)

    # Build full paths relative to the root directory
    full_structure = [(item_type, os.path.join(root_dir, path.lstrip('loot_box_game/'))) for item_type, path in structure]

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
