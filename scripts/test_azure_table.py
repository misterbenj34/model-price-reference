from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://azure.microsoft.com/en-us/pricing/details/azure-openai/", wait_until="networkidle")
    
    page.select_option("#region-selector", "sweden-central")
    page.select_option("#currency-selector", "eur")
    page.wait_for_timeout(3000)
    
    # Dump HTML of tables
    for idx, table in enumerate(page.query_selector_all("table")):
        print(f"--- Table {idx} ---")
        rows = table.query_selector_all("tr")
        for r in rows[:5]:
            cells = [c.inner_text().replace('\n', ' ').strip() for c in r.query_selector_all("td, th")]
            print(cells)
            
