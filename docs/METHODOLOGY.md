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

## Amazon Web Services (AWS) - Bedrock

**Target URL:** `https://aws.amazon.com/bedrock/pricing/`  
**Target Region:** Europe (Ireland) / `eu-west-1`  
**Target Currency:** US Dollar (USD)

### Challenges & Approach
Unlike Azure, AWS Bedrock's pricing page doesn't simply toggle DOM elements. The HTML source is heavily encoded (`&lt;td&gt;`), and pricing values are dynamically injected via separate internal API calls to AWS pricing services (e.g., `https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/...`). The frontend uses a complex JSON payload (`data-config`) to resolve localized strings.

To capture accurate AWS pricing without brittle reverse-engineering of their internal APIs:
1. **Model Discovery:**
   - Extract the HTML source and decode entities (replace `&lt;td&gt;` with `<td>`).
   - Use regex (`(?:<td>|^)([^<]+)</td><td>\{priceOf`) to locate all unique model names listed in the tables. This handles the frequent release of new models (e.g., the rapid iteration of Anthropic Claude from 3.0 to 4.6).
2. **Data Transformation & Standardization:**
   - AWS lists prices per **1,000 tokens**. To match the cross-provider schema, these values must be multiplied by 1,000 to represent prices per **1,000,000 (1M) tokens**.
3. **Deployment Modes Parsing:**
   - AWS defines specific routing mechanisms: `On-Demand`, `Global Cross-region`, and `Geo and In-region Cross-region`.
   - Batch inference pricing is typically available for cross-region deployments at exactly **50% of the On-Demand price**.
4. **Scripted Generation:**
   - The extraction logic (see `scripts/generate_aws.py`) maps the targeted providers (Anthropic, Mistral, Cohere, Qwen) to their corresponding pricing. 

### Automation Strategy
This extraction logic is intended to be encapsulated in Python scripts (`extract_azure.py`, `generate_aws.py`) and executed via a daily GitHub Actions cron job. The job will detect changes to the `.json` files and commit them to the repository if a price update has occurred. Additionally, the `compare_and_alert.py` script validates if any single price metric has fluctuated by more than 5%, triggering a Telegram notification.