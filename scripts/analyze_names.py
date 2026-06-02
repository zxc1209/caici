import re, json

with open('D:/python-learn/cai/web/js/players.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'^export default\s*', '', content.strip())
content = content.rstrip(';')
content = re.sub(r',\s*(\]|\})', r'\1', content)
data = json.loads(content)

firsts = set()
lasts = set()
multi = []

for p in data:
    name = p['name_en'].strip()
    parts = name.split()
    if len(parts) >= 1:
        firsts.add(parts[0])
    if len(parts) >= 2:
        lasts.add(parts[-1])
    if len(parts) > 2:
        multi.append(name)

print(f'Total players: {len(data)}')
print(f'Unique first names: {len(firsts)}')
print(f'Unique last names: {len(lasts)}')
print(f'Multi-word names (3+ words): {len(multi)}')
print()
print('=== ALL FIRST NAMES ===')
for n in sorted(firsts):
    print(n)
print()
print('=== ALL LAST NAMES ===')
for n in sorted(lasts):
    print(n)
print()
print('=== ALL MULTI-WORD NAMES ===')
for n in sorted(set(multi)):
    print(n)
