# LLM Price Reference Tracker

This repository tracks daily LLM pricing for major cloud providers: Azure, AWS, and Google Cloud Platform (GCP).

## Data Structure

The repository maintains individual JSON files for each provider to facilitate easy integration by external applications.

### File Format

Each file (`azure.json`, `aws.json`, `gcp.json`) follows this structure:

```json
{
  "provider": "ProviderName",
  "last_updated": "YYYY-MM-DD",
  "models": [
    {
      "name": "model-name",
      "price_per_1m_input_tokens": 0.00,
      "price_per_1m_output_tokens": 0.00,
      "currency": "USD"
    }
  ]
}
```

## Updates

Data is refreshed daily. This automation ensures that pricing data remains current for downstream applications.
