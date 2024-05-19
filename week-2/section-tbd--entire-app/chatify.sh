#!/bin/bash

# Constants
OUTPUT_FILE="$(pwd)/concatenated_python_files.txt"
GITIGNORE_FILE=".gitignore"  # Specify the path to your .gitignore file

# Function to clear the output file if it exists
clear_output_file() {
  > "$OUTPUT_FILE"
}

# Function to get the current directory
get_current_dir() {
  pwd
}

# Function to read .gitignore and prepare exclude options for find command
prepare_gitignore_excludes() {
  local gitignore_dir
  local gitignore_excludes=()

  gitignore_dir=$(dirname "$GITIGNORE_FILE")

  while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ "$line" =~ ^$ ]] && continue
    # Handle wildcard patterns and directory paths
    gitignore_excludes+=("-path" "$gitignore_dir/$line" "-prune" "-o")
  done < "$GITIGNORE_FILE"

  # Add common exclusions
  local common_excludes=(
    "-path ./venv" "-path ./__pycache__" "-path ./*.py[cod]"
    "-path ./*.egg-info" "-path ./*.env" "-path ./*env"
    "-path ./*cache*" "-path ./concatenated_python_files.txt"
  )

  gitignore_excludes+=("${common_excludes[@]}")

  echo "${gitignore_excludes[@]}"
}

# Function to run the tree command to give a layout of the file structure
generate_tree_output() {
  local tree_output
  tree_output=$(tree -I 'venv|__pycache__' -P '*.py')
  echo "$tree_output" > "$OUTPUT_FILE"
  echo -e "\n\n" >> "$OUTPUT_FILE"
}

# Function to concatenate Python files
concatenate_python_files() {
  local gitignore_excludes=("$@")
  find . \( ${gitignore_excludes[@]} -false -o -type f -name '*.py' \) -print | while read -r file; do
    # Ensure the file is a regular file (not a directory)
    if [[ -f $file && $file != "./$OUTPUT_FILE" ]]; then
      # Print a comment with the relative file path and name at the top of the output file
      echo "# File: $file" >> "$OUTPUT_FILE"
      # Concatenate the file contents to the output file
      cat "$file" >> "$OUTPUT_FILE"
      # Add a newline between files for readability
      echo -e "\n\n" >> "$OUTPUT_FILE"
    fi
  done
}

# Function to print completion message
print_completion_message() {
  echo "Concatenation complete. Output written to $OUTPUT_FILE"
}

# Main function to orchestrate the script
main() {
  clear_output_file
  local current_dir
  current_dir=$(get_current_dir)
  local gitignore_excludes
  gitignore_excludes=$(prepare_gitignore_excludes)
  generate_tree_output
  concatenate_python_files "${gitignore_excludes[@]}"
  print_completion_message
}

# Run the main function
main

echo "Copied to clipboard 📋"

cat "$OUTPUT_FILE" | pbcopy
