import os
import json
import re
import argparse

class ProjectStructureParser:
    def __init__(self, encoding='utf-8'):
        """
        Initialize the project structure parser.
        
        :param encoding: File encoding to use when reading the input file
        """
        self.encoding = encoding

    def parse_structure(self, input_file):
        """
        Parse a text file representing a directory structure.
        
        :param input_file: Path to the input text file
        :return: Nested dictionary representing the project structure
        """
        with open(input_file, 'r', encoding=self.encoding) as f:
            lines = f.readlines()
        
        # Remove empty lines and trailing whitespaces
        lines = [line.rstrip() for line in lines if line.strip()]
        
        return self._build_structure_dict(lines)

    def _build_structure_dict(self, lines):
        """
        Recursively build a nested dictionary from tree-style lines.
        
        :param lines: List of lines representing the directory structure
        :return: Nested dictionary 
        """
        # Extract the root directory name
        root_name = lines[0].rstrip('/').strip()
        root_dict = {root_name: {}}
        current_dict = root_dict[root_name]
        
        # Track the current path and hierarchy
        hierarchy_stack = [current_dict]
        current_hierarchy = []
        
        # Remove the root line and tree symbols from subsequent lines
        cleaned_lines = []
        for line in lines[1:]:
            # Remove tree symbols (├, └, │, ─)
            cleaned = re.sub(r'^[│├└─\s]+', '', line).strip()
            if cleaned:
                cleaned_lines.append(cleaned)
        
        for line in cleaned_lines:
            # Determine if it's a directory or file
            is_dir = line.endswith('/')
            
            # Clean the line (remove trailing /)
            clean_line = line.rstrip('/')
            
            if is_dir:
                # It's a directory
                # Adjust hierarchy based on depth
                while current_hierarchy and not self._is_parent_dir(current_hierarchy[-1], clean_line):
                    current_hierarchy.pop()
                    hierarchy_stack.pop()
                
                # Create or navigate to the directory
                current_location = hierarchy_stack[-1]
                current_location[clean_line] = {}
                
                # Update hierarchy
                current_hierarchy.append(clean_line)
                hierarchy_stack.append(current_location[clean_line])
            else:
                # It's a file
                # Place the file in the current directory
                current_location = hierarchy_stack[-1]
                current_location[clean_line] = None
        
        return root_dict

    def _is_parent_dir(self, parent, child):
        """
        Check if parent is a parent directory of child.
        
        :param parent: Parent directory name
        :param child: Potential child directory name
        :return: Boolean indicating if parent is a parent directory
        """
        # Simple implementation - in more complex scenarios, this might need refinement
        return child.startswith(parent) and child != parent

    def generate_json(self, input_file, output_file=None):
        """
        Generate JSON specification from the input text file.
        
        :param input_file: Path to the input text file
        :param output_file: Optional path to save the JSON file
        :return: JSON representation of the project structure
        """
        # Parse the structure
        structure = self.parse_structure(input_file)
        
        # Convert to JSON
        json_str = json.dumps(structure, indent=4)
        
        # Save to file if output path is provided
        if output_file:
            with open(output_file, 'w', encoding=self.encoding) as f:
                f.write(json_str)
        
        return json_str

class ProjectStructureCreator:
    @staticmethod
    def create_project_structure(tree_spec, base_path=None, confirm=True):
        """
        Create a project folder and file structure based on a dictionary specification.
        
        :param tree_spec: Dictionary representing the folder/file structure
        :param base_path: Base directory where the structure will be created
        :param confirm: Whether to ask for user confirmation before creating
        """
        # Determine the base path
        if base_path is None:
            base_path = os.getcwd()
        
        # Find the root directory name (first key in the dictionary)
        if len(tree_spec) != 1:
            raise ValueError("Input structure should have a single root directory")
        
        root_name = list(tree_spec.keys())[0]
        root_structure = tree_spec[root_name]
        full_path = os.path.join(base_path, root_name)
        
        # Preview the structure
        print("Proposed Project Structure:")
        ProjectStructureCreator._preview_structure(root_structure, root_name)
        
        # Ask for confirmation if enabled
        if confirm:
            response = input(f"\nCreate project structure in '{full_path}'? (y/n): ").lower().strip()
            if response != 'y':
                print("Project creation cancelled.")
                return
        
        # Create the structure
        def create_path(path_parts, is_file=False):
            full_path = os.path.join(base_path, *path_parts)
            if is_file:
                # Ensure parent directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                # Create empty file
                open(full_path, 'a').close()
            else:
                os.makedirs(full_path, exist_ok=True)

        def process_tree(current_tree, current_path=None):
            current_path = current_path or [root_name]
            
            for name, content in current_tree.items():
                full_path = current_path + [name]
                
                if isinstance(content, dict):
                    # This is a directory
                    create_path(full_path)
                    # Recursively process subdirectories
                    process_tree(content, full_path)
                elif content is None:
                    # This is an empty file
                    create_path(full_path, is_file=True)
                elif isinstance(content, str):
                    # This is a file with optional initial content
                    create_path(full_path, is_file=True)
                    file_path = os.path.join(base_path, *full_path)
                    with open(file_path, 'w') as f:
                        f.write(content)

        # Validate input
        if not isinstance(root_structure, dict):
            raise ValueError("Tree specification must be a dictionary")

        # Create the structure
        process_tree(root_structure)
        print(f"\nProject structure created in '{full_path}'")

    @staticmethod
    def _preview_structure(structure, root_name, indent='', printed_dirs=None):
        """
        Print a preview of the project structure.
        
        :param structure: Dictionary representing the project structure
        :param root_name: Name of the root directory
        :param indent: Current indentation level
        :param printed_dirs: Set to track printed directories and avoid duplicates
        """
        if printed_dirs is None:
            printed_dirs = set()

        # Only print root name if it hasn't been printed before
        if root_name not in printed_dirs:
            print(f"{indent}{root_name}/")
            printed_dirs.add(root_name)
        
        next_indent = indent + '    '
        
        for name, content in structure.items():
            if content is None:
                # File
                print(f"{next_indent}{name}")
            elif isinstance(content, dict):
                # Prevent duplicating directory names in the preview
                if name not in printed_dirs:
                    print(f"{next_indent}{name}/")
                    printed_dirs.add(name)
                
                # Recursively preview subdirectories
                ProjectStructureCreator._preview_structure(content, name, next_indent, printed_dirs)

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Create project folder structure')
    parser.add_argument('input_file', help='Text file with project structure specification')
    parser.add_argument('-d', '--directory', 
                        help='Base directory to create project structure (default: current directory)')
    parser.add_argument('-j', '--json-output', 
                        help='Optional output path for generated JSON specification')
    parser.add_argument('-e', '--encoding', default='utf-8',
                        help='File encoding (default: utf-8)')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='Skip confirmation and create project structure')
    args = parser.parse_args()

    try:
        # Initialize parser with specified encoding
        parser = ProjectStructureParser(encoding=args.encoding)
        
        # Generate JSON (optionally save to file)
        json_spec = parser.generate_json(args.input_file, args.json_output)
        
        # Parse JSON specification and create project structure
        tree_spec = json.loads(json_spec)
        
        # Determine base directory
        base_dir = args.directory or os.getcwd()
        
        # Create project structure
        ProjectStructureCreator.create_project_structure(
            tree_spec, 
            base_path=base_dir, 
            confirm=not args.yes
        )
    
    except Exception as e:
        print(f"Error creating project structure: {e}")

if __name__ == '__main__':
    main()