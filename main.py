import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.call_function import call_function

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of a specific file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to retrieve content from, relative to the working directory.",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file and returns the output.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specific file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    ),
)


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file
    ]
)

# Capture the prompt from command line arguments or exit the program
user_prompt = sys.argv[1] if len(sys.argv) > 1 else None
if not user_prompt:
    print("Usage: python main.py <prompt>")
    sys.exit(1)

messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

# Initialize the Google GenAI client
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents=messages, config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
    ),
)

# Add verbose flag if specified
verbose = '--verbose' in sys.argv
if hasattr(response, "function_calls") and response.function_calls:
    function_call = response.function_calls[0]
    function_call_result = call_function(function_call, verbose=verbose)
    # Check for function response
    if not (hasattr(function_call_result, "parts") and function_call_result.parts and hasattr(function_call_result.parts[0], "function_response") and hasattr(function_call_result.parts[0].function_response, "response")):
        raise RuntimeError("Fatal: No function response in call_function result.")
    response_dict = function_call_result.parts[0].function_response.response
    # Print only the result value if it exists and is a string
    result_value = response_dict.get("result")
    if verbose:
        print(f"-> {result_value}")
    else:
        print(result_value)
else:
    print(getattr(response, "text", ""))

if verbose:
    print(f"User prompt: {user_prompt}")
    # Also print the prompt tokens and response tokens
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")