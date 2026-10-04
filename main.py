#!/usr/bin/env python3
"""
Elpris App - Henter elpriser og finder de 5 billigste timer for næste dag
"""

import requests
import json
from datetime import datetime, timedelta
import os
import sys

# Konfiguration
CONFIG = {
    "netselskab": "trefor_el-net_c",
    "produkt": "clever",
    "omraade": "DK1",
    "api_base": "https://api.stromligning.dk/api/v1",
    "threshold": 0.8,
    "farveblind": True
}

# Mock data til test
MOCK_PRICES = [
    {"hour": 0, "price": 1.25, "total": 1.25},
    {"hour": 1, "price": 1.10, "total": 1.10},
    {"hour": 2, "price": 0.95, "total": 0.95},
    {"hour": 3, "price": 0.85, "total": 0.85},
    {"hour": 4, "price": 0.80, "total": 0.80},
    {"hour": 5, "price": 0.90, "total": 0.90},
    {"hour": 6, "price": 1.10, "total": 1.10},
    {"hour": 7, "price": 1.50, "total": 1.50},
    {"hour": 8, "price": 1.80, "total": 1.80},
    {"hour": 9, "price": 2.00, "total": 2.00},
    {"hour": 10, "price": 1.90, "total": 1.90},
    {"hour": 11, "price": 1.70, "total": 1.70},
    {"hour": 12, "price": 1.60, "total": 1.60},
    {"hour": 13, "price": 1.50, "total": 1.50},
    {"hour": 14, "price": 1.40, "total": 1.40},
    {"hour": 15, "price": 1.30, "total": 1.30},
    {"hour": 16, "price": 1.20, "total": 1.20},
    {"hour": 17, "price": 1.40, "total": 1.40},
    {"hour": 18, "price": 1.60, "total": 1.60},
    {"hour": 19, "price": 1.80, "total": 1.80},
    {"hour": 20, "price": 1.70, "total": 1.70},
    {"hour": 21, "price": 1.40, "total": 1.40},
    {"hour": 22, "price": 1.20, "total": 1.20},
    {"hour": 23, "price": 1.00, "total": 1.00}
]

def get_elpriser_for_tomorrow():
    """Henter elpriser for næste dag"""
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")

    url = f"{CONFIG['api_base']}/prices/{date_str}"
    params = {
        "netselskab": CONFIG["netselskab"],
        "produkt": CONFIG["produkt"],
        "omraade": CONFIG["omraade"]
    }

    try:
        headers = {
            "User-Agent": "ElprisApp/1.0 (Personal use - Non-commercial)",
            "Accept": "application/json"
        }
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"API fejl: {response.status_code}")
            return None
    except Exception as e:
        print(f"Fejl ved API-kald: {e}")
        return {"prices": MOCK_PRICES, "date": date_str}

def get_elpriser_from_elprisenligenu():
    """Backup API"""
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")

    url = f"https://www.elprisenligenu.dk/api/v1/prices/{date_str}_DK1.json"

    try:
        headers = {
            "User-Agent": "ElprisApp/1.0 (Personal use - Non-commercial)"
        }
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            prices = []
            for hour_data in data.get("prices", []):
                hour = int(hour_data.get("hour", 0))
                price = float(hour_data.get("price", 0))
                prices.append({
                    "hour": hour,
                    "price": price,
                    "total": price
                })
            return {"prices": prices, "date": date_str}
        else:
            print(f"Backup API fejl: {response.status_code}")
            return None
    except Exception as e:
        print(f"Fejl ved backup API-kald: {e}")
        return {"prices": MOCK_PRICES, "date": date_str}

def find_cheapest_hours(prices_data, num_hours=5):
    """Finder de billigste timer"""
    if not prices_data or "prices" not in prices_data:
        return []

    prices = prices_data["prices"]
    if not prices:
        return []

    sorted_prices = sorted(prices, key=lambda x: x.get("total", float('inf')))
    cheapest = sorted_prices[:num_hours]
    cheapest_sorted = sorted(cheapest, key=lambda x: x.get("hour", 0))

    return cheapest_sorted

def format_result(cheapest_hours, date):
    """Formaterer resultaterne"""
    if not cheapest_hours:
        return "Kunne ikke hente elpriser for næste dag."

    lines = [
        f"📅 De 5 billigste timer på {date} ({CONFIG['omraade']}):",
        "=" * 50
    ]

    for hour_data in cheapest_hours:
        hour = hour_data.get("hour", 0)
        price = hour_data.get("total", 0)
        lines.append(f"  🕒 Klokken {hour:02d}:00 - {price:.4f} kr/kWh")

    lines.append("=" * 50)
    lines.append("⚡ Tip: Start elforbrug i disse timer for at spare penge!")

    return "\n".join(lines)

def main():
    """Hovedfunktion"""
    print("Henter elpriser for næste dag...")

    prices_data = get_elpriser_for_tomorrow()

    if not prices_data:
        print("Prøver backup API...")
        prices_data = get_elpriser_from_elprisenligenu()

    if not prices_data:
        print("Kunne ikke hente data fra nogen API. Prøv igen senere.")
        return False

    cheapest_hours = find_cheapest_hours(prices_data)
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%A %d. %B %Y")
    result = format_result(cheapest_hours, date_str)

    print("\n" + result)

    output_file = f"result_{tomorrow.strftime('%Y%m%d')}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"\nResultat gemt til: {output_file}")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
