import json
import urllib.request
import re
import html
import ssl
import os
import sys
from datetime import datetime

# Comprehensive GCP Vertex AI Pricing (Generative AI)
# This handles GCP's special logic:
# - Pricing differs based on context length (<= 128k/200k vs > 128k/200k).
# - We map this to our 1M token schema by adding specific input/output variants 
#   (e.g., input_long_context, cached_input_long_context, etc.)
# - GCP has 3 deployment modes: Standard, Priority, Flex/Batch.
# - Batch pricing on GCP is exactly 50% of Standard pricing for Gemini models.
#
# Parsing note: the GCP pricing page has no stable `data-text` section markers
# any more (changed Oct 2026). We instead select tables by their header row:
# the Standard tables are the Gemini tables whose price columns mention
# "200K" and do NOT say "with Priority" / "with Flex/Batch".

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../gcp.json')
PRICING_URL = "https://cloud.google.com/vertex-ai/generative-ai/pricing?hl=en"
MIN_MODELS = 5  # refuse to overwrite gcp.json with fewer models than this


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


def _txt(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def iter_standard_gemini_tables(content):
    """Yield (header, rows) for each Standard-tier Gemini pricing table."""
    for m in re.finditer(r'<table', content):
        end = content.find('</table>', m.start())
        if end == -1:
            continue
        table = content[m.start():end]
        if 'Gemini' not in table:
            continue
        raw_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
        if not raw_rows:
            continue
        header = [_txt(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', raw_rows[0], re.DOTALL)]
        head_str = ' | '.join(header)
        # Standard tier: price columns with the 200K threshold, no "with Priority" / "with Flex"
        if '200K' not in head_str or 'Price' not in head_str:
            continue
        if 'with Priority' in head_str or 'with Flex' in head_str or 'Flex/Batch' in head_str:
            continue
        rows = [[_txt(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)]
                for r in raw_rows[1:]]
        yield header, rows


def normalize_model_name(name):
    return (name.replace('2.5Flash', '2.5 Flash')
                .replace('ProComputer', 'Pro Computer')
                .replace('Use-Preview', 'Use Preview')
                .replace('\xa0', ' ')
                .strip())


def parse_models(content):
    models_data = {}

    for header, rows in iter_standard_gemini_tables(content):
        has_region = len(header) > 2 and header[2].lower() == 'region'
        current_model = None
        for cols in rows:
            if not cols:
                continue
            if cols[0]:
                # New model block
                name = normalize_model_name(cols[0])
                if not name.startswith('Gemini'):
                    current_model = None
                    continue
                current_model = name
                if len(cols) < 2:
                    continue
                type_str, rest = cols[1], cols[2:]
            else:
                if not current_model or len(cols) < 2:
                    continue
                type_str, rest = cols[1], cols[2:]

            if has_region:
                if not rest or rest[0] != 'Global':
                    continue
                rest = rest[1:]

            prices = rest[:4] + [None] * (4 - len(rest[:4]))
            p1, p2, p3, p4 = prices
            models_data.setdefault(current_model, {'prices_under': {}, 'prices_over': {}})
            d = models_data[current_model]

            t = type_str.lower()
            is_output = 'output' in t and ('text' in t or 'response' in t)
            is_audio_only = ('audio' in t and 'text' not in t and 'video' not in t and 'image' not in t)
            is_input_main = 'input' in t and not is_output and not is_audio_only

            val_under = clean_price(p1)
            val_over = clean_price(p2)
            val_cached_under = clean_price(p3)
            val_cached_over = clean_price(p4)

            if is_output:
                if val_under is not None: d['prices_under']['output'] = val_under
                if val_over is not None: d['prices_over']['output'] = val_over
            elif is_audio_only:
                if val_under is not None: d['prices_under']['audio_input'] = val_under
                if val_over is not None: d['prices_over']['audio_input'] = val_over
                if val_cached_under is not None: d['prices_under']['cached_audio_input'] = val_cached_under
                if val_cached_over is not None: d['prices_over']['cached_audio_input'] = val_cached_over
            elif is_input_main:
                if val_under is not None: d['prices_under']['input'] = val_under
                if val_over is not None: d['prices_over']['input'] = val_over
                if val_cached_under is not None: d['prices_under']['cached_input'] = val_cached_under
                if val_cached_over is not None: d['prices_over']['cached_input'] = val_cached_over

    models = []
    for name, data in models_data.items():
        # Exclude purely image models or special preview ones that don't have standard input/output
        if 'input' not in data['prices_under'] or 'output' not in data['prices_under']:
            continue
        # Exclude Live API models
        if "Live API" in name:
            continue
        models.append(create_gcp_model(name, data['prices_under'], data['prices_over']))
    return models


def generate_gcp_pricing():
    print("Fetching GCP HTML...")
    content = fetch_html(PRICING_URL)

    models = parse_models(content)

    # Safety net: never overwrite a good gcp.json with an empty/partial parse
    if len(models) < MIN_MODELS:
        print(f"ERROR: only {len(models)} GCP models parsed (expected >= {MIN_MODELS}). "
              f"Page structure probably changed; gcp.json NOT written.", file=sys.stderr)
        sys.exit(1)

    gcp_data = {
      "provider": "GCP",
      "last_updated": datetime.now().strftime("%Y-%m-%d"),
      "region": "us-central1 (Iowa) - Global Defaults",
      "currency": "USD",
      "special_logic": "GCP scales pricing based on context length (<= 128K/200K vs > 128K/200K). These are mapped using '_long_context' suffix. Flex/Batch is exactly 50% of Standard.",
      "models": models
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(gcp_data, f, indent=2)

    print(f"Successfully generated gcp.json with {len(models)} models.")


if __name__ == "__main__":
    generate_gcp_pricing()
