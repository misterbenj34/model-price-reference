#!/usr/bin/env python3
# bedrock_anthropic_scraper.py
import requests, json, re
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict
from typing import Optional

URL = "https://aws.amazon.com/bedrock/pricing/"
OUTPUT = "bedrock_anthropic_pricing.json"
HEADERS = {"User-Agent":"Mozilla/5.0"}

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def try_parse_json_blob(s: str):
    try:
        return json.loads(s)
    except:
        try:
            return json.loads(s.replace("'", '"'))
        except:
            return None

def normalize_region_key(k: str) -> str:
    return re.sub(r'[^a-z0-9]', '', (k or "").lower())

def match_region(page_key: str, wanted: Optional[list]=None):
    # return raw page_key (caller can map); keep simple
    return page_key

def extract_price_from_span(span):
    # span may have data-amount attribute with {"regional":{...}} or numeric text
    data = span.get("data-amount") or span.get("data-amount-json") or ""
    if data:
        parsed = try_parse_json_blob(data)
        if parsed:
            # prefer 'regional' map if present
            regional = parsed.get("regional") or parsed.get("regions") or {}
            return regional
    # fallback: text like "$0.123"
    txt = span.get_text(" ", strip=True)
    m = re.search(r"\$([\d,]+(?:\.\d+)?)", txt)
    if m:
        return {"global": float(m.group(1).replace(",", ""))}
    return {}

def find_anthropic_section(soup: BeautifulSoup):
    # find provider card or heading that contains "Anthropic"
    # search for headings or links
    for tag in soup.find_all(["h2","h3","h4","div","section"]):
        txt = tag.get_text(" ", strip=True).lower()
        if "anthropic" in txt:
            # return nearest ancestor section that contains pricing rows
            return tag.find_parent()
    # fallback: search for provider list items
    for a in soup.find_all("a"):
        if "anthropic" in (a.get_text() or "").lower():
            return a.find_parent()
    return None

def parse_rows_from_section(section):
    models = []
    # find all table rows under section
    rows = section.find_all("tr")
    if not rows:
        # fallback: find div rows that look like model entries
        rows = section.find_all(lambda t: t.name in ("div","li") and "model" in (t.get("class") or []))
    for tr in rows:
        tds = tr.find_all(["td","th"])
        if not tds or len(tds) < 2:
            continue
        model_name = tds[0].get_text(" ", strip=True)
        pricing_td = tds[1]
        # walk children to map labels -> span
        last_label = None
        price_map = defaultdict(dict)  # label -> regional map
        for child in pricing_td.children:
            text = child.get_text(" ", strip=True) if hasattr(child, "get_text") else str(child).strip()
            if text:
                if re.search(r'\bCached\s*Input\b', text, flags=re.I):
                    last_label = "cached_input"
                elif re.search(r'\bInput\b', text, flags=re.I):
                    last_label = "input"
                elif re.search(r'\bOutput\b', text, flags=re.I):
                    last_label = "output"
            if hasattr(child, "find_all"):
                span = child if child.name=="span" and "price-data" in (child.get("class") or []) else child.find("span", class_="price-data")
                if span:
                    regional = extract_price_from_span(span)
                    key = last_label or "input"
                    price_map[key] = regional
                    last_label = None
        if price_map:
            models.append({"name": model_name, "prices": price_map})
    return models

def build_output(models):
    out = {
        "provider": "AWS Bedrock (Anthropic)",
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
        "currency": "USD",
        "models": []
    }
    for m in models:
        # convert regional dicts to lists
        deployments = []
        # single deployment assumed
        regions = []
        for label, regional in m["prices"].items():
            for rk, val in regional.items():
                regions.append({"region": rk, "field": label, "value": val})
        out["models"].append({"name": m["name"], "regions_raw": regions})
    return out

def main():
    html = fetch_html(URL)
    soup = BeautifulSoup(html, "html.parser")
    section = find_anthropic_section(soup)
    if not section:
        raise RuntimeError("Could not locate Anthropic provider block in page HTML. The page may render pricing client-side.")
    models = parse_rows_from_section(section)
    if not models:
        raise RuntimeError("No model rows found for Anthropic in the located section.")
    out = build_output(models)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("Saved", OUTPUT)

if __name__ == "__main__":
    main()