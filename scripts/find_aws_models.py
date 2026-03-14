import re

with open("aws_pricing_en.txt", "r") as f:
    text = f.read()

# AWS pricing HTML encodes the table rows.
# e.g., <tr><td>Claude Opus 4.6</td><td>...
# which comes out as &lt;tr&gt;&lt;td&gt;Claude Opus 4.6&lt;/td&gt;&lt;td&gt;
# or just Claude Opus 4.6&lt;/td&gt;&lt;td&gt;

matches = re.findall(r'(?:&lt;td&gt;|^)([^&]+)&lt;/td&gt;&lt;td&gt;{priceOf', text)
models = set()
for m in matches:
    clean = m.replace('&lt;tr&gt;', '').replace('&lt;td&gt;', '').strip()
    if clean:
        models.add(clean)

for m in sorted(models):
    print(m)
