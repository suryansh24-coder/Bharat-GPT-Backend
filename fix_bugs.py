import re

with open('bharatgpt.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# FIX: Remove backslash before ${...} inside template literals
# The file has \${...} which escapes the template expression
# We need ${...} for the expressions to actually evaluate
# ============================================================

# Replace \${ with ${ globally — these are all inside template literals
content = content.replace('\\${', '${')
print("Fix applied: Removed backslash escaping from template literal expressions")

# Count how many replacements
count = content.count('${')
print(f"Total template expressions now: {count}")

with open('bharatgpt.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved successfully!")
