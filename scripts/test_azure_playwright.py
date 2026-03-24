from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://azure.microsoft.com/en-us/pricing/details/azure-openai/", wait_until="networkidle")
    
    region_opts = page.query_selector_all("#region-selector option")
    print("Region options:")
    for opt in region_opts:
        text = opt.text_content().strip()
        val = opt.get_attribute("value")
        if "sweden" in val.lower() or "sweden" in text.lower():
            print(f"  {text} -> {val}")
            
    currency_opts = page.query_selector_all("#currency-selector option")
    print("Currency options:")
    for opt in currency_opts:
        text = opt.text_content().strip()
        val = opt.get_attribute("value")
        if "eur" in val.lower() or "euro" in text.lower():
            print(f"  {text} -> {val}")

