import os

def write_file(working_directory, file_path, content):
    # Resolve working_directory as absolute path
    working_directory = os.path.abspath(working_directory)
    
    # If file_path is absolute, use as is; if relative, join with working_directory
    if os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    else:
        file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    # Ensure file_path is within working_directory
    if not os.path.commonpath([working_directory, file_path]) == working_directory:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(file_path):
        # If the file does not exist, create the necessary directories
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: {str(e)}'