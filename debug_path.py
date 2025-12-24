import os
from pathlib import Path

# Check from ragbot_backend directory
backend_dir = os.path.join(os.path.dirname(__file__), "ragbot_backend")
docs_path = os.path.join(backend_dir, "..", "..", "docs")
docs_path = os.path.abspath(docs_path)

print(f"Backend directory: {backend_dir}")
print(f"Docs path: {docs_path}")
print(f"Docs path exists: {os.path.exists(docs_path)}")
print(f"Docs path is directory: {os.path.isdir(docs_path)}")

if os.path.exists(docs_path) and os.path.isdir(docs_path):
    files = []
    for root, dirs, file_list in os.walk(docs_path):
        for file in file_list:
            if file.endswith(('.md', '.txt', '.html')):
                file_path = os.path.abspath(os.path.join(root, file))
                files.append(f"file://{file_path}")
    print(f"Found {len(files)} files: {files}")
else:
    print("Docs directory not found")
    print(f"Looking in: {docs_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir(os.path.dirname(docs_path))}")