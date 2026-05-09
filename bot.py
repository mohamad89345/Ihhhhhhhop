from keep_alive import keep_alive

keep_alive()


# -*- coding: utf-8 -*-

import requests
import time
import schedule
import threading
import re

# ================= TOKEN =================
TOKEN = "1703029786:bbiuG31Rk8FNxCWdz_0O9JcSnGAg0HruATk"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

groups = set()


# ================= GET UPDATES =================
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30}

    if offset:
        params["offset"] = offset

    return requests.get(url, params=params).json()


# ================= SEND MESSAGE =================
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


# ================= GOLD PRICE =================
def get_gold_price():
    try:
        url = "https://milli.gold/"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers, timeout=10)
        html = r.text

        prices = re.findall(r"\d{2,3},\d{3},\d{3}", html)

        if not prices:
            return "نامشخص"

        price = int(prices[0].replace(",", "")) // 10
        return f"{price:,}"

    except:
        return "نامشخص"


# ================= DOLLAR PRICE (PERSISTENT) =================
def get_dollar_price():
    # ===== Exir =====
    try:
        url = "https://api.exir.io/v1/ticker?symbol=usdt-irt"
        r = requests.get(url, timeout=10).json()

        price = r.get("last")
        if price:
            return f"{int(float(price)):,}"
    except:
        pass

    # ===== Nobitex =====
    try:
        url = "https://api.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls"
        r = requests.get(url, timeout=10).json()

        price = r["stats"]["usdt-rls"]["latest"]
        if price:
            return f"{int(price):,}"
    except:
        pass

    return "نامشخص"


# ================= TEXT =================
def get_all_prices():
    return (
        "💰 قیمت لحظه‌ای بازار\n\n"
        f"🥇 طلا: {get_gold_price()} تومان\n"
        f"💵 دلار: {get_dollar_price()} تومان"
    )


def get_gold_only():
    return f"🥇 طلا: {get_gold_price()} تومان"


def get_dollar_only():
    return f"💵 دلار: {get_dollar_price()} تومان"


# ================= AUTO SEND =================
def auto_send():
    text = get_all_prices()

    for g in list(groups):
        try:
            send_message(g, text)
        except:
            pass


schedule.every(20).minutes.do(auto_send)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


threading.Thread(target=run_schedule, daemon=True).start()


# ================= HANDLE MESSAGES =================
def handle(updates):
    for u in updates.get("result", []):

        msg = u.get("message")
        if not msg:
            continue

        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if msg["chat"]["type"] in ["group", "supergroup"]:
            groups.add(chat_id)

        if "طلا" in text:
            send_message(chat_id, get_gold_only())

        if "دلار" in text:
            send_message(chat_id, get_dollar_only())


# ================= MAIN LOOP =================
def main():
    offset = None

    while True:
        try:
            updates = get_updates(offset)

            if updates.get("result"):
                offset = updates["result"][-1]["update_id"] + 1
                handle(updates)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(1)


if __name__ == "__main__":
    main()