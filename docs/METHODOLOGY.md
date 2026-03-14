# Extraction Methodology

This document outlines the extraction methodology used to gather, parse, and structure LLM pricing data from major cloud providers.

## Azure OpenAI

**Target URL:** `https://azure.microsoft.com/en-us/pricing/details/azure-openai/`  
**Target Region:** Sweden Central  
**Target Currency:** Euro (EUR)

### Challenges & Approach
The Azure pricing page dynamically calculates and renders prices via JavaScript based on user selections (Region, Currency). A static HTTP request (like `curl` or `requests` in Python) will only return the default USD pricing for the default region.

To capture accurate localized pricing:
1. **Headless Browser Execution:** We must use a tool capable of executing JavaScript (e.g., Playwright, Puppeteer, or a CLI wrapper).
2. **DOM Interaction:** 
   - Locate the "Region" dropdown element and select "Sweden Central".
   - Locate the "Currency" dropdown element and select "Euro Zone – Euro (€) EUR".
   - Wait for the pricing tables to re-render.
3. **Data Parsing:**
   - Iterate through the structured pricing tables for each model series (e.g., GPT-5.2, GPT-5.1, o3, GPT-4o).
   - Identify the "Deployment Type" (Global, Data Zone, Regional).
   - Extract the individual token prices per 1M tokens (Input, Cached Input, Output, Batch Input, etc.).
4. **Data Formatting:**
   - Map the extracted strings to floats (removing `$` or `€` symbols).
   - Structure the output into the standardized JSON schema defined in the `README.md`.

### Automation Strategy
This extraction logic is intended to be encapsulated in a script (see `scripts/extract_azure.py`) and executed via a daily GitHub Actions cron job. The job will detect changes to the `azure.json` file and commit them to the repository if a price update has occurred.