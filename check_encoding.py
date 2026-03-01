with open('bharatgpt.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find handleSendMessage function body start
idx = content.find('async function handleSendMessage()')
func_body_start = content.find('{', idx)

# Count braces from the function body start
depth = 0
end_pos = func_body_start
for i in range(func_body_start, len(content)):
    ch = content[i]
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            end_pos = i
            break

# Get line number of end
line_num = content[:end_pos].count('\n') + 1
print(f"handleSendMessage function body closes at line {line_num}")
print(f"Context around end:")
# Show 3 lines before and after
lines = content[:end_pos+50].split('\n')
for i in range(max(0, line_num-4), min(len(lines), line_num+3)):
    print(f"  Line {i+1}: {lines[i].rstrip()[:100]}")
