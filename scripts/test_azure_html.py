import urllib.request
import re

url = "https://azure.microsoft.com/en-us/pricing/details/azure-openai/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    html = response.read().decode('utf-8')

print(f"HTML length: {len(html)}")
tables = re.findall(r'<table.*?>(.*?)</table>', html, re.DOTALL)
print(f"Found {len(tables)} tables.")
