import random  # Wird genutzt für zufälliges Bluffen

def price_oligopol(market_data):
    """
    Oligopol-Bot für dynamische Preissetzung im simulierten Markt.
    Ziel: Anpassung des Preises in jeder Runde auf Basis vergangener Verkäufe,
    Gegnerverhalten und Marktdruck, um den Gewinn zu maximieren.

    Argumente:
        market_data (list): Liste von Dictionaries mit historischen Daten zu jeder Runde.
                            Jede Runde enthält Infos zu Preisen, Verkäufen, Lager, etc.

    Rückgabe:
        float: Der Preis, den der Bot in der aktuellen Runde setzen will.
    """

    # === Konfiguration – feste Einstellungen ===
    DEFAULT_PRICE = 36.0         # Startpreis, falls keine Daten vorhanden
    MIN_PRICE = 30.0             # Untergrenze für den Preis
    MAX_PRICE = 100.0            # Obergrenze für den Preis
    EXPLORATION_PRICES = [34.99, 37.99, 40.99]  # Testpreise zu Beginn
    UNDERCUT_STEP = 0.5          # Wie stark Gegner unterboten werden sollen
    BLUFF_DELTA = 3.0            # Bluffaufschlag (wenn wir stark wirken wollen)
    BLUFF_CHANCE = 0.1           # 10 % Bluff-Wahrscheinlichkeit
    HISTORY_DEPTH = 5            # Wie viele Runden für Gegneranalyse betrachtet werden
    SALE_WINDOW = 3              # Wie viele Runden für Verkaufsanalyse verwendet werden

    # === Sonderfall: erste Runde → Standardpreis ===
    if not market_data:
        return DEFAULT_PRICE

    # === Aktuelle Runde: Werte aus der letzten Runde extrahieren ===
    last_round = market_data[-1]
    period = last_round.get("period", 0)
    remaining = last_round.get("remaining_rounds", 100)
    inventory = last_round.get("own_inventory", 20)
    own_price = last_round.get("own_price", DEFAULT_PRICE)

    # === Gegnerpreise & Gegnernamen ermitteln ===
    opponent_prices = []
    opponent_names = []
    for key in last_round:
        if key.endswith("_price") and not key.startswith("own"):
            opponent_prices.append(last_round[key])
            opponent_names.append(key.replace("_price", ""))

    # === Marktanalyse: Minimum- & Durchschnittspreis der Gegner ===
    min_opp_price = min(opponent_prices, default=DEFAULT_PRICE)
    avg_opp_price = (
        sum(opponent_prices) / len(opponent_prices)
        if opponent_prices else DEFAULT_PRICE
    )

    # === Explorationsphase: Testpreise in den ersten Runden ===
    if period < len(EXPLORATION_PRICES):
        return EXPLORATION_PRICES[period]

    # === Eigene Verkaufszahlen der letzten Runden analysieren ===
    recent_sales = [
        r.get("own_sold", 0)
        for r in market_data[-SALE_WINDOW:]
    ]
    sale_sum = sum(recent_sales)

    # === Gegneranalyse: Wer hat uns unterboten? ===
    undercutters = set()
    for r in market_data[-HISTORY_DEPTH:]:
        my_price = r.get("own_price", DEFAULT_PRICE)
        for name in opponent_names:
            opp_price = r.get(f"{name}_price", DEFAULT_PRICE)
            if opp_price < my_price:
                undercutters.add(name)

    # === Verkaufsdruck berechnen: Lagerbestand / verfügbare Runden ===
    adjusted_remaining = max(remaining + 10, 1)  # Puffer, um nicht zu früh panisch zu werden
    pressure = inventory / adjusted_remaining

    # === Preisentscheidung: Basierend auf Verkaufsanalyse & Gegnerverhalten ===
    new_price = own_price  # Ausgangspunkt

    if sale_sum == 0:
        # Keine Verkäufe: aggressiv unterbieten
        new_price = max(min_opp_price - UNDERCUT_STEP, MIN_PRICE)
    elif sale_sum >= 2:
        # Gute Verkäufe: moderat erhöhen
        new_price = min(own_price + 1.0, MAX_PRICE)
    else:
        # Mittlere Verkäufe: Gegner beobachten
        if len(undercutters) >= 2:
            # Viele Unterbieter: leicht unterbieten
            new_price = min_opp_price - 0.01
        else:
            # Wenige Unterbieter: leicht über dem Marktmittelpreis anbieten
            new_price = avg_opp_price + 0.5

    # === Optionaler Bluff bei geringem Verkaufsdruck ===
    if pressure < 0.7 and random.random() < BLUFF_CHANCE:
        new_price += BLUFF_DELTA  # Preis künstlich höher setzen, um Stärke zu zeigen

    # === Feinanpassung je nach Verkaufsdruck (Lager & Zeit) ===
    if pressure > 1.6:
        new_price -= 2.0  # Viel Lager, wenig Zeit → Preis senken
    elif pressure < 0.5:
        new_price += 0.5  # Wenig Lager, viel Zeit → moderat erhöhen

    # === Rückgabe: Gültiger, gerundeter Preis ===
    return round(max(min(new_price, MAX_PRICE), MIN_PRICE), 2)
