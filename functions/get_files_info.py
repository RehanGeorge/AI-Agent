import os

def get_files_info(working_directory, directory=None):
    # Always resolve working_directory as absolute path
    working_directory = os.path.abspath(working_directory)
    if directory is None:
        directory = working_directory
    else:
        # If directory is absolute, use as is; if relative, join with working_directory
        if os.path.isabs(directory):
            directory = os.path.abspath(directory)
        else:
            directory = os.path.abspath(os.path.join(working_directory, directory))

    # Ensure directory is within working_directory
    if not os.path.commonpath([working_directory, directory]) == working_directory:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(directory):
        return f'Error: "{directory}" is not a directory'

    try:
        entries = []
        for entry in os.listdir(directory):
            entry_path = os.path.join(directory, entry)
            is_dir = os.path.isdir(entry_path)
            file_size = os.path.getsize(entry_path)
            entries.append(f"- {entry}: file_size={file_size} bytes, is_dir={is_dir}")
        return "\n".join(entries)
    except Exception as e:
        return f'Error: {str(e)}'

