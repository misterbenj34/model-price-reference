import json
from datetime import datetime

# Updating AWS Bedrock Pricing script to include all Anthropic, Mistral, Cohere, Qwen models
# and the new deployment types.
# Note: AWS uses "Cross-region inference" which routes across regions within a geography (Geo and In-region) or globally (Global).

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
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 3.00,
            "output": 15.00,
            "batch_input": 1.50,
            "batch_output": 7.50
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 3.00,
            "output": 15.00,
            "batch_input": 1.50,
            "batch_output": 7.50
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
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 0.80,
            "output": 4.00,
            "batch_input": 0.40,
            "batch_output": 2.00
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 0.80,
            "output": 4.00,
            "batch_input": 0.40,
            "batch_output": 2.00
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
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 15.00,
            "output": 75.00,
            "batch_input": 7.50,
            "batch_output": 37.50
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 15.00,
            "output": 75.00,
            "batch_input": 7.50,
            "batch_output": 37.50
          }
        }
      ]
    },
    {
      "name": "Anthropic Claude 3 Sonnet",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 3.00,
            "output": 15.00
          }
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 3.00,
            "output": 15.00,
            "batch_input": 1.50,
            "batch_output": 7.50
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 3.00,
            "output": 15.00,
            "batch_input": 1.50,
            "batch_output": 7.50
          }
        }
      ]
    },
    {
      "name": "Anthropic Claude 3 Haiku",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.25,
            "output": 1.25
          }
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 0.25,
            "output": 1.25,
            "batch_input": 0.125,
            "batch_output": 0.625
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 0.25,
            "output": 1.25,
            "batch_input": 0.125,
            "batch_output": 0.625
          }
        }
      ]
    },
    {
      "name": "Anthropic Claude 2.1",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 8.00,
            "output": 24.00
          }
        }
      ]
    },
    {
      "name": "Anthropic Claude 2.0",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 8.00,
            "output": 24.00
          }
        }
      ]
    },
    {
      "name": "Anthropic Claude Instant",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.80,
            "output": 2.40
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
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 2.00,
            "output": 6.00,
            "batch_input": 1.00,
            "batch_output": 3.00
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 2.00,
            "output": 6.00,
            "batch_input": 1.00,
            "batch_output": 3.00
          }
        }
      ]
    },
    {
      "name": "Mistral Large (24.02)",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 4.00,
            "output": 12.00
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
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.45,
            "batch_input": 0.075,
            "batch_output": 0.225
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.45,
            "batch_input": 0.075,
            "batch_output": 0.225
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
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.45,
            "batch_input": 0.075,
            "batch_output": 0.225
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.45,
            "batch_input": 0.075,
            "batch_output": 0.225
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
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20,
            "batch_input": 0.075,
            "batch_output": 0.10
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20,
            "batch_input": 0.075,
            "batch_output": 0.10
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
      "name": "Cohere Command",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 1.50,
            "output": 2.00
          }
        }
      ]
    },
    {
      "name": "Cohere Command Light",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.30,
            "output": 0.60
          }
        }
      ]
    },
    {
      "name": "Cohere Embed (English)",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.10
          }
        }
      ]
    },
    {
      "name": "Cohere Embed (Multilingual)",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.10
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
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 0.35,
            "output": 0.40,
            "batch_input": 0.175,
            "batch_output": 0.20
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 0.35,
            "output": 0.40,
            "batch_input": 0.175,
            "batch_output": 0.20
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
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20,
            "batch_input": 0.075,
            "batch_output": 0.10
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20,
            "batch_input": 0.075,
            "batch_output": 0.10
          }
        }
      ]
    },
    {
      "name": "Qwen 2.5 14B",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20
          }
        },
        {
          "type": "Global Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20,
            "batch_input": 0.075,
            "batch_output": 0.10
          }
        },
        {
          "type": "Geo and In-region Cross-region",
          "pricing_1m_tokens": {
            "input": 0.15,
            "output": 0.20,
            "batch_input": 0.075,
            "batch_output": 0.10
          }
        }
      ]
    },
    {
      "name": "Qwen 2 72B Instruct",
      "deployments": [
        {
          "type": "On-Demand",
          "pricing_1m_tokens": {
            "input": 0.35,
            "output": 0.40
          }
        }
      ]
    }
  ]
}

with open('../aws.json', 'w') as f:
    json.dump(bedrock_data, f, indent=2)