from IPython.display import Markdown, display
import os

def display_markdown_file(file_name):
    try:
        # Get the current working directory
        current_dir = os.getcwd()
        
        # Construct the file path
        file_path = os.path.join(current_dir, file_name)
        
        # Read and display the file content
        with open(file_path, 'r') as markdown_file:
            content = markdown_file.read()
            # Use IPython.display to render the markdown
            display(Markdown(content))
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found in the current directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Specify the markdown file name you want to read
    markdown_file_name = "report.md"  # Replace with the actual file name
    
    display_markdown_file(markdown_file_name)