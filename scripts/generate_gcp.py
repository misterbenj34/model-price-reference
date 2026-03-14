import json
from datetime import datetime

# Comprehensive GCP Vertex AI Pricing (Generative AI)
# This handles GCP's special logic:
# - Pricing differs based on context length (<= 128k/200k vs > 128k/200k).
# - We map this to our 1M token schema by adding specific input/output variants 
#   (e.g., input_under_128k, input_over_128k, etc.)
# - GCP has 3 deployment modes: Standard, Priority, Flex/Batch.
# - Batch pricing on GCP is exactly 50% of Standard pricing for Gemini models.

def create_gcp_model(name, prices_under, prices_over, priority_multiplier=1.0):
    # Prices under/over are dicts: {"input": X, "cached_input": Y, "output": Z, "audio_input": A}
    
    def calc_batch(prices):
        return {k: round(v * 0.5, 4) for k, v in prices.items()}
        
    def calc_priority(prices):
        # Priority often implies provisioned throughput (node-hours), 
        # but for the sake of the token-based schema, if it scales linearly we map it,
        # otherwise we just put placeholder multipliers or N/A. Let's use standard token prices 
        # for standard & batch. For priority, GCP usually charges per node-hour, not per token.
        # But to fit the token schema, we'll represent Standard and Flex/Batch.
        pass

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
        },
        {
            "type": "Priority",
            "pricing_1m_tokens": {
                "note": "Priority deployment is typically billed per Node-Hour (Provisioned Throughput) rather than per-token."
            }
        }
    ]
    
    return {
        "name": name,
        "deployments": deployments
    }

models = []

# --- Gemini 3.1 & 3 --- (context boundary: 200k)
models.append(create_gcp_model(
    "Gemini 3.1 Pro Preview",
    prices_under={"input": 2.00, "cached_input": 0.20, "output": 12.00},
    prices_over={"input": 4.00, "cached_input": 0.40, "output": 18.00}
))

models.append(create_gcp_model(
    "Gemini 3.1 Flash-Lite Preview",
    prices_under={"input": 0.25, "audio_input": 0.50, "cached_input": 0.03, "cached_audio_input": 0.05, "output": 1.50},
    prices_over={"input": 0.25, "audio_input": 0.50, "cached_input": 0.03, "cached_audio_input": 0.05, "output": 1.50}
))

models.append(create_gcp_model(
    "Gemini 3 Pro Preview",
    prices_under={"input": 2.00, "cached_input": 0.20, "output": 12.00},
    prices_over={"input": 4.00, "cached_input": 0.40, "output": 18.00}
))

models.append(create_gcp_model(
    "Gemini 3 Flash Preview",
    prices_under={"input": 0.50, "audio_input": 1.00, "cached_input": 0.05, "cached_audio_input": 0.10, "output": 3.00},
    prices_over={"input": 0.50, "audio_input": 1.00, "cached_input": 0.05, "cached_audio_input": 0.10, "output": 3.00}
))

# --- Gemini 2.5 --- (context boundary: 128k)
models.append(create_gcp_model(
    "Gemini 2.5 Pro",
    prices_under={"input": 1.25, "cached_input": 0.13, "output": 10.00},
    prices_over={"input": 2.50, "cached_input": 0.25, "output": 15.00}
))

models.append(create_gcp_model(
    "Gemini 2.5 Flash",
    prices_under={"input": 0.30, "audio_input": 1.00, "cached_input": 0.03, "cached_audio_input": 0.10, "output": 2.50},
    prices_over={"input": 0.30, "audio_input": 1.00, "cached_input": 0.03, "cached_audio_input": 0.10, "output": 2.50}
))

# Compile the final JSON
gcp_data = {
  "provider": "GCP",
  "last_updated": datetime.now().strftime("%Y-%m-%d"),
  "region": "us-central1 (Iowa) - Global Defaults",
  "currency": "USD",
  "special_logic": "GCP scales pricing based on context length (<= 128K/200K vs > 128K/200K). These are mapped using '_long_context' suffix. Flex/Batch is exactly 50% of Standard. Priority is provisioned per node-hour.",
  "models": models
}

with open('../gcp.json', 'w') as f:
    json.dump(gcp_data, f, indent=2)
