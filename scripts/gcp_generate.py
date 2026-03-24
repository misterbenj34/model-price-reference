import json
import urllib.request
import re
import html
import ssl
import os
from datetime import datetime

# Comprehensive GCP Vertex AI Pricing (Generative AI)
# This handles GCP's special logic:
# - Pricing differs based on context length (<= 128k/200k vs > 128k/200k).
# - We map this to our 1M token schema by adding specific input/output variants 
#   (e.g., input_long_context, cached_input_long_context, etc.)
# - GCP has 3 deployment modes: Standard, Priority, Flex/Batch.
# - Batch pricing on GCP is exactly 50% of Standard pricing for Gemini models.

def create_gcp_model(name, prices_under, prices_over):
    # Build the pricing_1m_tokens payload combining under/over
    pricing_std = {}
    pricing_batch = {}
    
    # Under context threshold
    for k, v in prices_under.items():
        pricing_std[f"{k}"] = v
        pricing_batch[f"batch_{k}"] = round(v * 0.5, 4)
        
    # Over context threshold
    for k, v in prices_over.items():
        if v is not None:
            pricing_std[f"{k}_long_context"] = v
            pricing_batch[f"batch_{k}_long_context"] = round(v * 0.5, 4)
            
    deployments = [
        {
            "type": "Standard",
            "pricing_1m_tokens": pricing_std
        },
        {
            "type": "Flex/Batch",
            "pricing_1m_tokens": pricing_batch
        }
    ]
    
    return {
        "name": name,
        "deployments": deployments
    }

def clean_price(p):
    if not isinstance(p, str): return None
    if p == 'N/A' or not p: return None
    p = p.replace('$', '').strip()
    try:
        return float(p)
    except:
        return None

def fetch_html(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    import gzip
    resp = urllib.request.urlopen(req, context=ctx)
    if resp.info().get('Content-Encoding') == 'gzip':
        return gzip.decompress(resp.read()).decode('utf-8')
    return resp.read().decode('utf-8')

def generate_gcp_pricing():
    print("Fetching GCP HTML...")
    content = fetch_html("https://cloud.google.com/vertex-ai/generative-ai/pricing?hl=en")
    
    models_data = {}
    
    sections = re.split(r'<h3[^>]*data-text="Gemini ', content)
    for sec in sections[1:]:
        standard_block = re.search(r'<h3[^>]*data-text="Standard"[^>]*>(.*?)</table>', sec, re.DOTALL)
        if standard_block:
            table_html = standard_block.group(1)
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
            current_model = None
            for r in rows:
                cols = re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)
                cols = [html.unescape(c).strip().replace('\n', ' ') for c in cols]
                cols = [re.sub(r'<[^>]+>', '', c) for c in cols]
                if not cols:
                    continue
                    
                if 'rowspan' in r:
                    current_model = cols[0]
                    # Normalize names
                    current_model = current_model.replace('2.5Flash', '2.5 Flash').replace('ProComputer', 'Pro Computer').replace('Use-Preview', 'Use Preview').replace('\xa0', ' ').strip()
                    if current_model not in models_data:
                        models_data[current_model] = {'prices_under': {}, 'prices_over': {}}
                    
                    if len(cols) > 1:
                        type_str = cols[1]
                        prices = cols[2:] + [None]*4
                        p1, p2, p3, p4 = prices[0], prices[1], prices[2], prices[3]
                    else:
                        continue
                else:
                    if current_model:
                        type_str = cols[0]
                        prices = cols[1:] + [None]*4
                        p1, p2, p3, p4 = prices[0], prices[1], prices[2], prices[3]
                    else:
                        continue
                        
                if current_model:
                    t = type_str.lower()
                    is_output = 'output' in t and ('text' in t or 'response' in t)
                    is_audio_only = ('audio' in t and 'text' not in t and 'video' not in t and 'image' not in t)
                    is_input_main = 'input' in t and not is_output and not is_audio_only
                    
                    val_under = clean_price(p1)
                    val_over = clean_price(p2)
                    val_cached_under = clean_price(p3)
                    val_cached_over = clean_price(p4)
                    
                    if is_output:
                        if val_under is not None: models_data[current_model]['prices_under']['output'] = val_under
                        if val_over is not None: models_data[current_model]['prices_over']['output'] = val_over
                    elif is_audio_only:
                        if val_under is not None: models_data[current_model]['prices_under']['audio_input'] = val_under
                        if val_over is not None: models_data[current_model]['prices_over']['audio_input'] = val_over
                        if val_cached_under is not None: models_data[current_model]['prices_under']['cached_audio_input'] = val_cached_under
                        if val_cached_over is not None: models_data[current_model]['prices_over']['cached_audio_input'] = val_cached_over
                    elif is_input_main:
                        if val_under is not None: models_data[current_model]['prices_under']['input'] = val_under
                        if val_over is not None: models_data[current_model]['prices_over']['input'] = val_over
                        if val_cached_under is not None: models_data[current_model]['prices_under']['cached_input'] = val_cached_under
                        if val_cached_over is not None: models_data[current_model]['prices_over']['cached_input'] = val_cached_over

    models = []
    
    # Filter and construct the list
    for name, data in models_data.items():
        # Exclude purely image models or special preview ones that don't have standard input/output
        if 'input' not in data['prices_under'] or 'output' not in data['prices_under']:
            continue
        # Also maybe exclude Live API for simplicity, or keep it if it maps. 
        if "Live API" in name:
            continue
            
        models.append(create_gcp_model(name, data['prices_under'], data['prices_over']))

    # Compile the final JSON
    gcp_data = {
      "provider": "GCP",
      "last_updated": datetime.now().strftime("%Y-%m-%d"),
      "region": "us-central1 (Iowa) - Global Defaults",
      "currency": "USD",
      "special_logic": "GCP scales pricing based on context length (<= 128K/200K vs > 128K/200K). These are mapped using '_long_context' suffix. Flex/Batch is exactly 50% of Standard.",
      "models": models
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../gcp.json')
    with open(output_path, 'w') as f:
        json.dump(gcp_data, f, indent=2)
        
    print(f"Successfully generated gcp.json with {len(models)} models.")

if __name__ == "__main__":
    generate_gcp_pricing()

