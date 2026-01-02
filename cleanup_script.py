import os
import re

root_dir = os.path.dirname(os.path.abspath(__file__))

patterns_to_remove = [
    r"",                       # folder name references
    r"https://[^'\"]*",        # old Vercel domain
]

# Optional: old baseUrl and projectName
patterns_to_replace = {
    r"baseUrl\s*:\s*'//'": "baseUrl: '/book/'",
    r"projectName\s*:\s*''": "projectName: 'book'",
}

for subdir, _, files in os.walk(root_dir):
    for file in files:
        filepath = os.path.join(subdir, file)

        # Skip binary files
        if filepath.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico', '.exe', '.dll')):
            continue

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content

        # Remove unwanted patterns
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content)

        # Replace specific config patterns
        for pattern, replacement in patterns_to_replace.items():
            content = re.sub(pattern, replacement, content)

        # Only write back if content was modified
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")