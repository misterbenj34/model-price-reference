import json
import urllib.request
import re
import html
import ssl
from datetime import datetime
import gzip
import os

def fetch_json(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        if resp.info().get('Content-Encoding') == 'gzip':
            return json.loads(gzip.decompress(resp.read()).decode('utf-8'))
        return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}

def fetch_html(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, context=ctx)
    if resp.info().get('Content-Encoding') == 'gzip':
        return html.unescape(gzip.decompress(resp.read()).decode('utf-8'))
    return html.unescape(resp.read().decode('utf-8'))

def parse_price(tag, price_maps, region_name):
    # e.g. bedrockfoundationmodels/bedrockfoundationmodels!RATEKEY!*!1000!opt
    parts = tag.split('!')
    service_id = parts[0].split('/')[0]
    rate_key = parts[1]
    
    if service_id not in price_maps:
        url = f"https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/{service_id}/USD/current/{service_id}.json"
        price_maps[service_id] = fetch_json(url)
    
    price_data = price_maps[service_id].get('regions', {}).get(region_name, {})
    if rate_key not in price_data:
        # Fallback to US West (Oregon) if region not found
        price_data = price_maps[service_id].get('regions', {}).get("US West (Oregon)", {})
        
    if rate_key not in price_data:
        return 0.0
        
    price = float(price_data[rate_key]['price'])
    
    # Check for multipliers like *!1000
    for i in range(2, len(parts)):
        if parts[i] == '*':
            # The next part should be the multiplier
            if i + 1 < len(parts) and parts[i+1].isdigit():
                price *= int(parts[i+1])
    
    return round(price, 3)

def create_model(name, input_price, output_price, batch_multiplier=0.5):
    batch_in = round(input_price * batch_multiplier, 3)
    batch_out = round(output_price * batch_multiplier, 3)
    
    return {
      "name": name,
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": input_price,
            "output": output_price
          }
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": input_price,
            "output": output_price,
            "batch_input": batch_in,
            "batch_output": batch_out
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": input_price,
            "output": output_price,
            "batch_input": batch_in,
            "batch_output": batch_out
          }
        }
      ]
    }

def generate_aws_pricing():
    print("Fetching HTML...")
    html_content = fetch_html("https://aws.amazon.com/bedrock/pricing/")
    
    price_maps = {}
    region_name = "EU (Ireland)" # Target Region
    
    # We want: Anthropic, Mistral, Cohere, Qwen
    target_brands = ['Claude', 'Mistral', 'Cohere', 'Command', 'Qwen']
    
    models = []
    seen_models = set()
    
    # Regex to find table rows with prices
    matches = re.findall(r'<tr>\s*<td>([^<]+)</td>\s*<td>\{priceOf!([^}]+)\}.*?\{priceOf!([^}]+)\}', html_content, re.IGNORECASE)
    
    for m in matches:
        name = m[0].strip()
        name = name.replace('Anthropic ', '') # Clean up
        if not any(b in name for b in target_brands):
            continue
            
        # Standardize names to match what we had
        if name.startswith('Claude'):
            name = 'Anthropic ' + name
        elif name.startswith('Command'):
            name = 'Cohere ' + name
        elif name.startswith('Qwen'):
            name = 'Qwen ' + name.replace('Qwen3', 'Qwen') # Normalizing Qwen names if needed
            
        if name in seen_models:
            continue
        
        seen_models.add(name)
        
        input_tag = m[1]
        output_tag = m[2]
        
        input_price = parse_price(input_tag, price_maps, region_name)
        output_price = parse_price(output_tag, price_maps, region_name)
        
        if input_price > 0 or output_price > 0:
            models.append(create_model(name, input_price, output_price))

    bedrock_data = {
      "provider": "AWS",
      "last_updated": datetime.now().strftime("%Y-%m-%d"),
      "region": "Europe (Ireland)",
      "currency": "USD",
      "models": models
    }
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../aws.json')
    with open(output_path, 'w') as f:
        json.dump(bedrock_data, f, indent=2)
    
    print(f"Successfully generated aws.json with {len(models)} models.")

if __name__ == "__main__":
    generate_aws_pricing()
