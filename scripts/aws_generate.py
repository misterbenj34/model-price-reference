import json
from datetime import datetime

# Comprehensive AWS Bedrock pricing (Europe Ireland, USD)
# Filtering exclusively for Anthropic, Mistral, Cohere, Qwen.

def create_model(name, input_price, output_price, batch_multiplier=0.5):
    # AWS batch pricing is exactly 50% of on-demand
    batch_in = round(input_price * batch_multiplier, 3)
    batch_out = round(output_price * batch_multiplier, 3)
    
    return {
      "name": name,
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": input_price,
            "output": output_price
          }
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": input_price,
            "output": output_price,
            "batch_input": batch_in,
            "batch_output": batch_out
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": input_price,
            "output": output_price,
            "batch_input": batch_in,
            "batch_output": batch_out
          }
        }
      ]
    }

models = []

# --- Anthropic ---
# Generation 4.6
models.append(create_model("Anthropic Claude Opus 4.6", 15.00, 75.00))
models.append(create_model("Anthropic Claude Opus 4.6 - Long Context", 15.00, 75.00))
models.append(create_model("Anthropic Claude Sonnet 4.6", 3.00, 15.00))
models.append(create_model("Anthropic Claude Sonnet 4.6 - Long Context", 3.00, 15.00))

# Generation 4.5
models.append(create_model("Anthropic Claude Opus 4.5", 15.00, 75.00))
models.append(create_model("Anthropic Claude Sonnet 4.5", 3.00, 15.00))
models.append(create_model("Anthropic Claude Sonnet 4.5 - Long Context", 3.00, 15.00))
models.append(create_model("Anthropic Claude Haiku 4.5", 0.80, 4.00))

# Generation 4
models.append(create_model("Anthropic Claude Opus 4.1", 15.00, 75.00))
models.append(create_model("Anthropic Claude Opus 4", 15.00, 75.00))
models.append(create_model("Anthropic Claude Sonnet 4", 3.00, 15.00))
models.append(create_model("Anthropic Claude Sonnet 4 - Long Context", 3.00, 15.00))

# Generation 3.x
models.append(create_model("Anthropic Claude 3.7 Sonnet", 3.00, 15.00))
models.append(create_model("Anthropic Claude 3.5 Sonnet v2", 3.00, 15.00))
models.append(create_model("Anthropic Claude 3.5 Sonnet", 3.00, 15.00))
models.append(create_model("Anthropic Claude 3.5 Haiku", 0.80, 4.00))
models.append(create_model("Anthropic Claude 3 Opus", 15.00, 75.00))
models.append(create_model("Anthropic Claude 3 Sonnet", 3.00, 15.00))
models.append(create_model("Anthropic Claude 3 Haiku", 0.25, 1.25))

# Legacy
models.append(create_model("Anthropic Claude 2.1", 8.00, 24.00))
models.append(create_model("Anthropic Claude 2.0", 8.00, 24.00))
models.append(create_model("Anthropic Claude Instant", 0.80, 2.40))


# --- Mistral AI ---
models.append(create_model("Mistral Large 2 (24.07)", 2.00, 6.00))
models.append(create_model("Mistral Large (24.02)", 4.00, 12.00))
models.append(create_model("Mistral Small (24.02)", 0.15, 0.45))
models.append(create_model("Mistral 8x7B Instruct", 0.15, 0.45))
models.append(create_model("Mistral 7B Instruct", 0.15, 0.20))


# --- Cohere ---
models.append(create_model("Cohere Command R+", 3.00, 15.00))
models.append(create_model("Cohere Command R", 0.50, 1.50))
models.append(create_model("Cohere Command", 1.50, 2.00))
models.append(create_model("Cohere Command Light", 0.30, 0.60))

# Embeddings (Input only)
cohere_embed_en = create_model("Cohere Embed (English)", 0.10, 0.0)
del cohere_embed_en["deployments"][0]["pricing_1m_tokens"]["output"]
del cohere_embed_en["deployments"][1]["pricing_1m_tokens"]["output"]
del cohere_embed_en["deployments"][1]["pricing_1m_tokens"]["batch_output"]
del cohere_embed_en["deployments"][2]["pricing_1m_tokens"]["output"]
del cohere_embed_en["deployments"][2]["pricing_1m_tokens"]["batch_output"]
models.append(cohere_embed_en)

cohere_embed_multi = create_model("Cohere Embed (Multilingual)", 0.10, 0.0)
del cohere_embed_multi["deployments"][0]["pricing_1m_tokens"]["output"]
del cohere_embed_multi["deployments"][1]["pricing_1m_tokens"]["output"]
del cohere_embed_multi["deployments"][1]["pricing_1m_tokens"]["batch_output"]
del cohere_embed_multi["deployments"][2]["pricing_1m_tokens"]["output"]
del cohere_embed_multi["deployments"][2]["pricing_1m_tokens"]["batch_output"]
models.append(cohere_embed_multi)


# --- Qwen ---
models.append(create_model("Qwen 2.5 72B", 0.35, 0.40))
models.append(create_model("Qwen 2.5 32B", 0.15, 0.20))
models.append(create_model("Qwen 2.5 14B", 0.15, 0.20))
models.append(create_model("Qwen 2 72B Instruct", 0.35, 0.40))


bedrock_data = {
  "provider": "AWS",
  "last_updated": datetime.now().strftime("%Y-%m-%d"),
  "region": "Europe (Ireland)",
  "currency": "USD",
  "models": models
}

with open('../aws.json', 'w') as f:
    json.dump(bedrock_data, f, indent=2)
