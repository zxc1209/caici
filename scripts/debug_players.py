import re, json

with open('D:/python-learn/cai/web/js/players.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the export wrapper
content = re.sub(r'^export default\s*', '', content.strip())
content = content.rstrip(';')
# Remove trailing commas (JS allows, JSON doesn't)
content = re.sub(r',\s*(\]|\})', r'\1', content)

try:
    data = json.loads(content)
    print('Success:', len(data))
except json.JSONDecodeError as e:
    print(f'Error at position {e.pos}: {e.msg}')
    start = max(0, e.pos - 100)
    end = min(len(content), e.pos + 100)
    print(repr(content[start:end]))
