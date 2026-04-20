import json
import re
import os
import urllib.request
from datetime import datetime

REGION = "sweden-central"

def parse_pricing_html(cell_html):
    """
    Extracts pricing from a raw HTML cell.
    Example: Input: <span class='price-data ' data-amount='{"regional":{"sweden-central":1.75...
    """
    result = {}
    
    # Each entry looks like: "Input: <span ... data-amount='{...}'"
    # We split by "<br />" or just search for all occurrences
    matches = re.finditer(r'([A-Za-z \-]+):\s*<span[^>]*data-amount=\'([^\']+)\'', cell_html)
    found_any = False
    for m in matches:
        key = m.group(1).strip().lower().replace(' ', '_').replace('-', '_')
        if key == 'input_text': key = 'input'
        if key == 'output_text': key = 'output'
        if key == 'cached_input_text': key = 'cached_input'
        if key == 'input_image': key = 'image_input'
        
        data_amount = json.loads(m.group(2))
        regional_prices = data_amount.get("regional", {})
        
        # Try to get the price for our target region, or fallback to us-east, or the first available
        price = regional_prices.get(REGION)
        if price is None and "us-east" in regional_prices:
            price = regional_prices.get("us-east")
        if price is None and regional_prices:
            price = list(regional_prices.values())[0]
            
        if price is not None:
            result[key] = float(price)
            found_any = True
            
    # If no "Input:" style spans were found, it might be a single price cell like Provisioned Throughput
    if not found_any:
        m = re.search(r'data-amount=\'([^\']+)\'', cell_html)
        if m:
            data_amount = json.loads(m.group(1))
            regional_prices = data_amount.get("regional", {})
            price = regional_prices.get(REGION)
            if price is None and regional_prices:
                price = list(regional_prices.values())[0]
            if price is not None:
                result['price'] = float(price)
                
    return result

def run_extraction():
    models = {}
    
    print("Fetching Azure pricing page...")
    url = "https://azure.microsoft.com/en-us/pricing/details/azure-openai/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch Azure page: {e}")
        return

    print("Parsing tables...")
    # Extract all tables
    tables = re.findall(r'<table.*?>(.*?)</table>', html, re.DOTALL)
    for table_html in tables:
        # Extract rows
        rows = re.findall(r'<tr.*?>(.*?)</tr>', table_html, re.DOTALL)
        if not rows:
            continue
            
        # Parse header
        headers = []
        for th in re.findall(r'<t[hd].*?>(.*?)</t[hd]>', rows[0], re.DOTALL):
            # Clean HTML from header
            clean_th = re.sub(r'<[^>]+>', '', th).replace('\n', ' ').strip()
            headers.append(clean_th)
            
        if not headers or ("Model" not in headers[0] and "Models" not in headers[0]):
            continue
            
        for row_html in rows[1:]:
            cells = re.findall(r'<td.*?>(.*?)</td>', row_html, re.DOTALL)
            if not cells or len(cells) < 2:
                continue
                
            model_full_name = re.sub(r'<[^>]+>', '', cells[0]).replace('\n', ' ').strip()
            if not model_full_name:
                continue
                
            # Identify deployment type from name
            dep_type = "Standard"
            base_name = model_full_name
            
            if base_name.endswith(" Global"):
                dep_type = "Global"
                base_name = base_name[:-7]
            elif base_name.endswith(" Data Zone"):
                dep_type = "Data Zone"
                base_name = base_name[:-10]
            elif base_name.endswith(" Regional"):
                dep_type = "Regional"
                base_name = base_name[:-9]
            elif base_name.endswith(" Data Zones"):
                dep_type = "Data Zone"
                base_name = base_name[:-11]
            
            prices = parse_pricing_html(cells[1])
            
            batch_prices = {}
            priority_prices = {}
            
            for i, header in enumerate(headers):
                if i < len(cells) and i > 0:
                    if "Batch API" in header:
                        b_prices = parse_pricing_html(cells[i])
                        for k, v in b_prices.items():
                            batch_prices[f"batch_{k}"] = v
                    elif "Priority" in header:
                        p_prices = parse_pricing_html(cells[i])
                        for k, v in p_prices.items():
                            priority_prices[f"priority_{k}"] = v
                            
            if base_name not in models:
                models[base_name] = []
                
            combined_prices = {**prices, **batch_prices, **priority_prices}

            if combined_prices:
                models[base_name].append({
                    "type": dep_type,
                    "pricing_1m_tokens": combined_prices
                })
        
    formatted_models = []
    for name, deployments in models.items():
        formatted_models.append({
            "name": name,
            "deployments": deployments
        })
        
    output = {
      "provider": "Azure",
      "last_updated": datetime.now().strftime("%Y-%m-%d"),
      "region": "Sweden Central",
      "currency": "USD",
      "models": formatted_models
    }
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../azure.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
        
    print(f"Successfully generated azure.json with {len(formatted_models)} models.")

if __name__ == "__main__":
    run_extraction()
