import json
import os
import sys
from datetime import datetime

# Threshold for alerts
THRESHOLD = 0.05

def compare_prices(old_data, new_data, changelog_entries):
    """Compares two pricing JSONs, returns a list of alerts if variation > 5%, and logs ALL changes."""
    alerts = []
    
    old_models = {m["name"]: m for m in old_data.get("models", [])}
    new_models = {m["name"]: m for m in new_data.get("models", [])}
    
    provider = new_data.get("provider", "Unknown Provider")
    
    for model_name, new_model in new_models.items():
        old_model = old_models.get(model_name)
        if not old_model:
            alerts.append(f"🆕 New model added to {provider}: *{model_name}*")
            changelog_entries.append(f"- **{provider} - {model_name}**: New model added.")
            continue
            
        old_deps = {d["type"]: d for d in old_model.get("deployments", [])}
        new_deps = {d["type"]: d for d in new_model.get("deployments", [])}
        
        for dep_type, new_dep in new_deps.items():
            old_dep = old_deps.get(dep_type)
            if not old_dep:
                changelog_entries.append(f"- **{provider} - {model_name} ({dep_type})**: New deployment added.")
                continue
            
            old_prices = old_dep.get("pricing_1m_tokens", {})
            new_prices = new_dep.get("pricing_1m_tokens", {})
            
            for price_key, new_price in new_prices.items():
                old_price = old_prices.get(price_key)
                if old_price is None or new_price is None or old_price == 0:
                    continue
                
                if old_price != new_price:
                    # Log to changelog unconditionally for ANY change
                    changelog_entries.append(
                        f"- **{provider} - {model_name} ({dep_type})** [{price_key}]: {old_price:.4f} -> {new_price:.4f}"
                    )
                    
                    # Alert if variation is >= 5%
                    variation = (new_price - old_price) / old_price
                    if abs(variation) >= THRESHOLD:
                        emoji = "🔺" if variation > 0 else "🔻"
                        alerts.append(
                            f"{emoji} *{provider} - {model_name} ({dep_type})*\n"
                            f"Price `{price_key}` changed by {variation*100:.1f}%\n"
                            f"Old: {old_price:.4f} -> New: {new_price:.4f}"
                        )
                    
    return alerts

def append_changelog(entries):
    if not entries:
        return
        
    changelog_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../CHANGELOG.md')
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    content = f"### {date_str}\n" + "\n".join(entries) + "\n\n"
    
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r') as f:
            existing = f.read()
    else:
        existing = "# Pricing Changelog\n\n"
        
    if "# Pricing Changelog" not in existing:
        existing = "# Pricing Changelog\n\n" + existing
        
    with open(changelog_path, 'w') as f:
        # Prepend new entries just below the header
        f.write(existing.replace("# Pricing Changelog\n\n", f"# Pricing Changelog\n\n{content}"))

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 global_compare_and_alert.py <old_json> <new_json>")
        sys.exit(1)
        
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    
    if not os.path.exists(old_file) or not os.path.exists(new_file):
        sys.exit(0)
        
    with open(old_file, 'r') as f:
        old_data = json.load(f)
        
    with open(new_file, 'r') as f:
        new_data = json.load(f)
        
    changelog_entries = []
    alerts = compare_prices(old_data, new_data, changelog_entries)
    
    if changelog_entries:
        append_changelog(changelog_entries)
    
    if alerts:
        print("🚨 *LLM Pricing Alert*\n\n" + "\n\n".join(alerts))

if __name__ == "__main__":
    main()
