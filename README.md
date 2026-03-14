# LLM Price Reference Tracker

This repository tracks daily LLM pricing for major cloud providers: Azure, AWS, and Google Cloud Platform (GCP).

## Data Structure

The repository maintains individual JSON files for each provider to facilitate easy integration by external applications. 

### File Format

Each file (`azure.json`, `aws.json`, `gcp.json`) follows this structure, detailing prices across different deployment modes (Global, Data Zone, Regional) and price variants (cached, batch, priority, etc.):

```json
{
  "provider": "ProviderName",
  "last_updated": "YYYY-MM-DD",
  "region": "RegionName",
  "currency": "EUR",
  "models": [
    {
      "name": "model-name",
      "deployments": [
        {
          "type": "Global",
          "pricing_1m_tokens": {
            "input": 0.00,
            "cached_input": 0.00,
            "output": 0.00,
            "batch_input": 0.00,
            "batch_cached_input": 0.00,
            "batch_output": 0.00,
            "priority_input": 0.00,
            "priority_output": 0.00
          }
        }
      ]
    }
  ]
}
```

## Updates and Alerting

Data is refreshed daily. This automation ensures that pricing data remains current for downstream applications. 

**Alerting Threshold**: The extraction scripts are configured to trigger an alert if the price of any model varies by more than **5%** compared to the previous day's data.