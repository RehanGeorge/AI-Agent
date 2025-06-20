import os
import subprocess

def run_python_file(working_directory, file_path):
    # Save the original file_path for error messages
    original_file_path = file_path
    # Resolve working_directory as absolute path
    working_directory = os.path.abspath(working_directory)
    
    # If file_path is absolute, use as is; if relative, join with working_directory
    if os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    else:
        file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    file_name = os.path.basename(file_path)

    # Ensure file_path is within working_directory
    if not os.path.commonpath([working_directory, file_path]) == working_directory:
        return f'Error: Cannot execute "{original_file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(file_path):
        return f'Error: File "{file_name}" not found.'

    if not file_path.endswith('.py'):
        return f'Error: "{file_name}" is not a Python file.'
    
    try:
        result = subprocess.run(
            ["python3", file_path],
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        response = []
        if output:
            response.append(f'STDOUT:\n{output}')
        if error:
            response.append(f'STDERR:\n{error}')
        if result.returncode != 0:
            response.append(f'Process exited with code {result.returncode}')
        if not response:
            return 'No output produced.'
        return '\n'.join(response)
    except subprocess.TimeoutExpired:
        return f'Error: executing Python file: Execution timed out after 30 seconds.'
    except Exception as e:
        return f'Error: executing Python file: {e}'