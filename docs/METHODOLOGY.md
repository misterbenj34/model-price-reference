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

## Google Cloud Platform (GCP) - Vertex AI

**Target URL:** `https://cloud.google.com/vertex-ai/generative-ai/pricing?hl=en`  
**Target Region:** us-central1 (Iowa) - Global Defaults  
**Target Currency:** US Dollar (USD)

### Challenges & Approach
Google Cloud's Vertex AI pricing introduces several unique billing vectors that differ significantly from Azure and AWS, particularly for their multimodal Gemini models (Gemini 3.1, Gemini 3, Gemini 2.5).

To capture accurate GCP pricing and map it to a standard `1M tokens` schema:
1. **Context Length Tiering (Special Logic):**
   - GCP charges different rates per token depending on the total length of the input prompt context. For example, prompts `<= 128K` or `<= 200K` tokens are billed at a standard rate, while prompts exceeding that threshold are billed at a higher rate.
   - **Approach:** We map this to our schema by appending a `_long_context` suffix to the pricing keys (e.g., `input_long_context`, `cached_input_long_context`, `output_long_context`) when the threshold is crossed.
2. **Multimodal Discrepancies:**
   - Text, Image, and Video inputs are grouped into a single base rate, but Audio input is frequently billed at a higher rate.
   - **Approach:** We extract and distinguish these by adding `audio_input` and `cached_audio_input` keys.
3. **Deployment Modes:**
   - **Standard:** Pay-as-you-go per 1M tokens.
   - **Flex/Batch:** Batch inference API, which is explicitly priced at exactly **50%** of the Standard rate.
   - **Priority:** Represents Provisioned Throughput (guaranteed capacity). This is generally billed per Node-Hour rather than per token. Our schema handles this by leaving token prices empty and appending a `note` clarifying the Node-Hour billing model.
4. **Scripted Generation:**
   - The extraction logic (see `scripts/generate_gcp.py`) programmatically applies the context length tiering and batch discount logic to output the standardized JSON format.

### Automation Strategy
This extraction logic is intended to be encapsulated in Python scripts (`extract_azure.py`, `generate_aws.py`, `generate_gcp.py`) and executed via a daily GitHub Actions cron job. The job will detect changes to the `.json` files and commit them to the repository if a price update has occurred. Additionally, the `compare_and_alert.py` script validates if any single price metric has fluctuated by more than 5%, triggering a Telegram notification.