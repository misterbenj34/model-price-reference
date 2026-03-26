import requests
import json
import re
from datetime import datetime
from collections import defaultdict
from typing import Optional

API_URL = "https://prices.azure.com/api/retail/prices"

EUROPE_REGIONS = [
    "northeurope",
    "westeurope",
    "swedencentral",
    "switzerlandnorth",
    "switzerlandwest",
    "francecentral",
    "francesouth",
    "germanywestcentral",
    "germanynorth",
    "norwayeast",
    "norwaywest",
    "uksouth",
    "ukwest",
    "italynorth",
    "polandcentral",
    "spaincentral",
]

CURRENCY = "EUR"
OUTPUT_FILE = "../azure_api.json"


def fetch_prices_for_region(region: str):
    """
    Fetch all prices for a given region in EUR.
    We filter by region + currency in the query,
    and filter for OpenAI client-side.
    """
    items = []
    params = {
        "$filter": f"armRegionName eq '{region}'",
        "currencyCode": CURRENCY,
        "api-version": "2023-01-01-preview",
    }

    next_link = API_URL

    while next_link:
        response = requests.get(next_link, params=params if next_link == API_URL else None)
        response.raise_for_status()
        data = response.json()

        items.extend(data.get("Items", []))
        next_link = data.get("NextPageLink")

        # After first request, params must not be reused with NextPageLink
        params = None

    return items


def is_openai_item(item: dict) -> bool:
    """
    Keep only Azure OpenAI-related meters.
    Adjust this if you see relevant items being dropped.
    """
    product = (item.get("productName") or "").lower()
    service = (item.get("serviceName") or "").lower()
    sku = (item.get("skuName") or "").lower()

    if "openai" in product or "openai" in service:
        return True
    if "gpt" in sku or "o3" in sku or "o1" in sku:
        return True
    return False


def classify_token_type(meter_name: str) -> Optional[str]:
    """
    Map meterName to one of: input, output, cached_input.
    """
    name = meter_name.lower()
    if "cached" in name:
        return "cached_input"
    if "input" in name:
        return "input"
    if "output" in name:
        return "output"
    return None


def detect_deployment_type(item: dict) -> str:
    """
    Distinguish Global vs Data Zone from productName/skuName/meterName.
    """
    product = (item.get("productName") or "").lower()
    sku = (item.get("skuName") or "").lower()
    meter = (item.get("meterName") or "").lower()

    if "data zone" in product or "data zone" in sku or "data zone" in meter:
        return "Data Zone"
    return "Global"


def extract_clean_model_name(raw_sku: str) -> str:
    """
    Azure SKU names often contain token types or deployment hints.
    We remove those and keep only the core model name.
    """
    if not raw_sku:
        return ""

    sku = raw_sku.lower()

    # Remove token-type suffixes
    sku = re.sub(r"\b(input|output|cached|cached input|cached_input)\b", "", sku)

    # Remove deployment hints
    sku = re.sub(r"\b(data zone|datazone|dz|glbl|global)\b", "", sku)

    # Remove extra spaces
    sku = re.sub(r"\s+", " ", sku).strip()

    return sku

def build_output_structure(all_region_prices: dict):
    """
    Convert raw API data into the final JSON structure.
    models[model_name][deployment_type][region][token_type] = price
    """
    models = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    for region, prices in all_region_prices.items():
        for item in prices:
            if not is_openai_item(item):
                continue

            meter_name = item.get("meterName") or ""
            token_type = classify_token_type(meter_name)
            if token_type is None:
                continue

            raw_sku = item.get("skuName", "")
            model_name = extract_clean_model_name(raw_sku)
            if not model_name:
                continue


            deployment_type = detect_deployment_type(item)
            raw_price = item.get("unitPrice")
            if raw_price is None:
                continue

            # Azure Retail API returns per-1K tokens even though it says "1M Tokens"
            price = raw_price * 1000


            models[model_name][deployment_type][region][token_type] = price

    # Build final JSON with merged pricing per region
    output_models = []
    for model_name, deployments in models.items():
        deployment_list = []
        for dep_type, region_data in deployments.items():
            region_entries = []
            for region, pricing in region_data.items():
                region_entries.append({
                    "region": region,
                    "pricing_1m_tokens": pricing
                })

            deployment_list.append({
                "type": dep_type,
                "regions": region_entries
            })

        output_models.append({
            "name": model_name,
            "deployments": deployment_list
        })

    return {
        "provider": "Azure",
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
        "currency": CURRENCY,
        "regions_included": EUROPE_REGIONS,
        "exchange_rate_note": (
            "Converted from USD base using Azure's internal FX rate for non-USD regions."
        ),
        "models": output_models
    }


def main():
    print("Fetching Azure OpenAI-related pricing for all European regions in EUR...\n")

    all_region_prices = {}

    for region in EUROPE_REGIONS:
        print(f"→ Fetching {region}...")
        prices = fetch_prices_for_region(region)
        all_region_prices[region] = prices
        print(f"  Retrieved {len(prices)} items.")

    print("\nBuilding final JSON structure...\n")
    output = build_output_structure(all_region_prices)

    #print(json.dumps(output, indent=2))
    # Save to JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)



if __name__ == "__main__":
    main()