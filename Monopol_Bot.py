
def price_monopol(market_data):
    import random

    # === Startpreis bei leerem Datensatz ===
    if len(market_data) == 0:
        return 60.0

    # Teamname automatisch ermitteln
    keys = market_data[0].keys()
    my_team = [k[:-6] for k in keys if k.endswith('_price')]
    my_team = my_team[0] if my_team else 'my_team'

    # Vergangene Preise und Verkäufe sammeln
    prices = []
    sold = []

    for entry in market_data:
        price = entry.get(f'{my_team}_price', None)
        quantity = entry.get(f'{my_team}_quantity', None)
        if price is not None and quantity is not None:
            prices.append(price)
            sold.append(quantity)

    # Anzahl vergangener Perioden
    t = len(prices)
    current_price = prices[-1]
    current_quantity = sold[-1]

    # Initiale Grenzwerte
    max_price = 150.0
    min_price = 1.0

    # Verkaufsquote berechnen
    success_rate = sum(sold[-10:]) / min(10, len(sold))

    # Schritt 1: Bewertung des letzten Preises
    if current_quantity == 1:
        # Verkauf erfolgreich → versuche nächstes Mal leicht höheren Preis
        next_price = current_price + 2.0
    else:
        # Kein Verkauf → Preis war zu hoch → senken
        next_price = current_price - 3.0

    # Schritt 2: Exploration alle 7 Runden
    if t % 7 == 0:
        next_price = current_price + random.uniform(-10, 10)

    # Schritt 3: Sanfte Anpassung je nach Verkaufsquote
    if success_rate < 0.4:
        next_price -= 5.0
    elif success_rate > 0.8:
        next_price += 3.0

    # Schritt 4: Glättung je nach Lagerdruck
    remaining_rounds = market_data[-1].get('remaining_rounds', 100)
    inventory = market_data[-1].get(f'{my_team}_inventory', 100)
    urgency_factor = inventory / max(1, remaining_rounds)

    if urgency_factor > 1.2:
        # viel Inventar, wenig Zeit → senken
        next_price *= 0.95
    elif urgency_factor < 0.5:
        # wenig Inventar, viel Zeit → erhöhen
        next_price *= 1.05

    # Schritt 5: Begrenzung und Rundung
    next_price = min(max(next_price, min_price), max_price)
    return round(next_price, 2)
