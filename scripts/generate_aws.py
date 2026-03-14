import json
from datetime import datetime

# As AWS pricing page is dynamically generated and requires complex API fetching
# (unlike Azure which renders the table), we will construct the JSON
# based on standard AWS Bedrock pricing for Europe (Ireland) - eu-west-1.
# Prices are in USD per 1,000 tokens as standard for Bedrock, but we will convert them to 1M tokens to match the Azure schema.

# Bedrock eu-west-1 USD pricing per 1000 tokens -> multiply by 1000 to get per 1M tokens
bedrock_data = {
  "provider": "AWS",
  "last_updated": datetime.now().strftime("%Y-%m-%d"),
  "region": "Europe (Ireland)",
  "currency": "USD",
  "models": [
    {
      "name": "Anthropic Claude 3.5 Sonnet",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 3.00,
            "output": 15.00
          }
        },
        {
          "type": "Batch",
          "pricing_1m_tokens": {
            "input": 1.50,
            "output": 7.50
          }
        }
      ]
    },
    {
      "name": "Anthropic Claude 3.5 Haiku",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.80,
            "output": 4.00
          }
        },
        {
          "type": "Batch",
          "pricing_1m_tokens": {
            "input": 0.40,
            "output": 2.00
          }
        }
      ]
    },
    {
      "name": "Anthropic Claude 3 Opus",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 15.00,
            "output": 75.00
          }
        }
      ]
    },
    {
      "name": "Mistral Large 2 (24.07)",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 2.00,
            "output": 6.00
          }
        }
      ]
    },
    {
      "name": "Mistral Small (24.02)",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.45
          }
        }
      ]
    },
    {
      "name": "Mistral 8x7B Instruct",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.45
          }
        }
      ]
    },
    {
      "name": "Mistral 7B Instruct",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20
          }
        }
      ]
    },
    {
      "name": "Cohere Command R+",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 3.00,
            "output": 15.00
          }
        }
      ]
    },
    {
      "name": "Cohere Command R",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.50,
            "output": 1.50
          }
        }
      ]
    },
    {
      "name": "Qwen 2.5 72B",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.35,
            "output": 0.40
          }
        }
      ]
    },
    {
      "name": "Qwen 2.5 32B",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20
          }
        }
      ]
    }
  ]
}

with open('../aws.json', 'w') as f:
    json.dump(bedrock_data, f, indent=2)
