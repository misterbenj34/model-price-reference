import json
import re
import os
from playwright.sync_api import sync_playwright
from datetime import datetime

def parse_pricing_string(pricing_str):
    result = {}
    matches = re.finditer(r'([A-Za-z \-]+):\s*€([\d,\.]+)', pricing_str)
    for m in matches:
        key = m.group(1).strip().lower().replace(' ', '_').replace('-', '_')
        val = float(m.group(2).replace(',', ''))
        
        if key == 'input_text': key = 'input'
        if key == 'output_text': key = 'output'
        if key == 'cached_input_text': key = 'cached_input'
        if key == 'input_image': key = 'image_input'
        
        result[key] = val
    return result

def run_extraction():
    models = {}
    
    print("Starting Playwright extraction for Azure...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://azure.microsoft.com/en-us/pricing/details/azure-openai/", wait_until="networkidle")
        
        print("Selecting region and currency...")
        page.select_option("#region-selector", "sweden-central")
        page.select_option("#currency-selector", "eur")
        page.wait_for_timeout(4000) # Give time for JS to render
        
        print("Parsing tables...")
        tables = page.query_selector_all("table")
        for table in tables:
            # Check if this table has a "Model" header
            first_row = table.query_selector("tr")
            if not first_row:
                continue
                
            headers = [th.inner_text().replace('\n', ' ').strip() for th in first_row.query_selector_all("th, td")]
            if not headers or ("Model" not in headers[0] and "Models" not in headers[0]):
                continue
                
            for row in table.query_selector_all("tr")[1:]:
                cells = [td.inner_text().replace('\n', ' ').strip() for td in row.query_selector_all("td")]
                if not cells or len(cells) < 2:
                    continue
                    
                model_full_name = cells[0]
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
                
                prices = parse_pricing_string(cells[1])
                
                batch_prices = {}
                priority_prices = {}
                
                for i, header in enumerate(headers):
                    if i < len(cells) and i > 0:
                        if "Batch API" in header:
                            b_prices = parse_pricing_string(cells[i])
                            for k, v in b_prices.items():
                                batch_prices[f"batch_{k}"] = v
                        elif "Priority" in header:
                            p_prices = parse_pricing_string(cells[i])
                            for k, v in p_prices.items():
                                priority_prices[f"priority_{k}"] = v
                        elif "Pricing" in header and i > 1: # Some tables have a third column for another pricing
                            # Already handled in basic pricing if it's the second column. If not, maybe it's something else.
                            pass
                                
                if base_name not in models:
                    models[base_name] = []
                    
                combined_prices = {**prices, **batch_prices, **priority_prices}
                
                # If no prices were extracted via regex, maybe it's a raw price like "€0.000103"
                if not combined_prices:
                    m = re.search(r'€([\d,\.]+)', cells[1])
                    if m:
                        val = float(m.group(1).replace(',', ''))
                        combined_prices['price'] = val

                if combined_prices:
                    models[base_name].append({
                        "type": dep_type,
                        "pricing_1m_tokens": combined_prices
                    })
                    
        browser.close()
        
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
      "currency": "EUR",
      "models": formatted_models
    }
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../azure.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
        
    print(f"Successfully generated azure.json with {len(formatted_models)} models.")

if __name__ == "__main__":
    run_extraction()

