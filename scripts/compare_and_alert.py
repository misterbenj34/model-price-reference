import json
import os
import requests
import sys

# Threshold for alerts
THRESHOLD = 0.05

def send_telegram_alert(message):
    """Sends an alert to Telegram if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set in environment."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Telegram credentials not found. Skipping alert send.")
        print(f"ALERT WOULD BE: {message}")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}", file=sys.stderr)

def compare_prices(old_data, new_data):
    """Compares two pricing JSONs and returns a list of alerts if variation > 5%."""
    alerts = []
    
    # Create lookup dicts for easy comparison
    old_models = {m["name"]: m for m in old_data.get("models", [])}
    new_models = {m["name"]: m for m in new_data.get("models", [])}
    
    provider = new_data.get("provider", "Unknown Provider")
    
    for model_name, new_model in new_models.items():
        old_model = old_models.get(model_name)
        if not old_model:
            alerts.append(f"🆕 New model added to {provider}: *{model_name}*")
            continue
            
        old_deps = {d["type"]: d for d in old_model.get("deployments", [])}
        new_deps = {d["type"]: d for d in new_model.get("deployments", [])}
        
        for dep_type, new_dep in new_deps.items():
            old_dep = old_deps.get(dep_type)
            if not old_dep:
                continue
            
            old_prices = old_dep.get("pricing_1m_tokens", {})
            new_prices = new_dep.get("pricing_1m_tokens", {})
            
            for price_key, new_price in new_prices.items():
                old_price = old_prices.get(price_key)
                if old_price is None or new_price is None or old_price == 0:
                    continue
                
                variation = (new_price - old_price) / old_price
                if abs(variation) >= THRESHOLD:
                    emoji = "🔺" if variation > 0 else "🔻"
                    alerts.append(
                        f"{emoji} *{provider} - {model_name} ({dep_type})*\n"
                        f"Price `{price_key}` changed by {variation*100:.1f}%\n"
                        f"Old: €{old_price:.4f} -> New: €{new_price:.4f}"
                    )
                    
    return alerts

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compare_and_alert.py <old_json> <new_json>")
        sys.exit(1)
        
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    
    if not os.path.exists(old_file):
        print(f"Old file {old_file} not found. Assuming first run. No comparisons made.")
        sys.exit(0)
        
    with open(old_file, 'r') as f:
        old_data = json.load(f)
        
    with open(new_file, 'r') as f:
        new_data = json.load(f)
        
    alerts = compare_prices(old_data, new_data)
    
    if alerts:
        message = "🚨 *LLM Pricing Alert*\n\n" + "\n\n".join(alerts)
        send_telegram_alert(message)
    else:
        print("No significant pricing changes detected.")

if __name__ == "__main__":
    main()