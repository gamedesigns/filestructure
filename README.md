# File Structure Utility

Utility to create file and folder structure from input project outline in tree format.

```sh
maindir_game/
├── Cargo.toml
└── src/
    ├── main.rs
    ├── plugins/
    │   ├── player_plugin.rs

```
## Example Usages

### Normal Usage (with Confirmation)
```sh
python project_structure_generator.py project_structure.txt
```

### Skip Confirmation
```sh
python project_structure_generator.py project_structure.txt -y
```

### Specify a Different Base Directory
```sh
python project_structure_generator.py project_structure.txt -d /path/to/projects
```

### Save JSON Specification
```sh
python project_structure_generator.py project_structure.txt -j project_spec.json
```

## Script Execution

When you run the script, it will:

1. Parse the input file
2. Preview the proposed project structure
3. Ask for confirmation (unless `-y` is used)
4. Create the project structure in the specified or current directory
