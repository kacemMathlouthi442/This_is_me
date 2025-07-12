import re
import requests
from datetime import datetime
import random
import phonenumbers
from phonenumbers import NumberParseException
from Others import spoofing_numbers, spoofing_services, services, vip_spoof

def get_random_lines(count=40):
    with open('numbers.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]  # keep all lines, remove empty ones
    if len(lines) < count:
        raise ValueError(f"The file only has {len(lines)} non-empty lines. Cannot pick {count}.")
    return random.sample(lines, count)

def set_message(spoofing_numbers):
    msg = """🦅 *AORUS Spoofing Numbers List*       

📦 *Amazon* — `"""+spoofing_numbers[0]+"""`  
🟢 *Google Support* — `"""+spoofing_numbers[1]+"""`    
📘 *Facebook* — `"""+spoofing_numbers[2]+"""`         
🐦 *Twitter Support* — `"""+spoofing_numbers[3]+"""`  
🚕 *Uber Support* — `"""+spoofing_numbers[4]+"""`     
🏦 *Chase Bank* — `"""+spoofing_numbers[5]+"""`
🏦 *Bank Of America* — `"""+spoofing_numbers[6]+"""`
🏦 *Wells Fargo* — `"""+spoofing_numbers[7]+"""`
🏦 *U\.S\. Bank* — `"""+spoofing_numbers[8]+"""`
🏛 *Truist Bank* — `"""+spoofing_numbers[9]+"""`
🏛 *Citibank* — `"""+spoofing_numbers[10]+"""`
🏦 *Pnc Bank* — `"""+spoofing_numbers[11]+"""`
💳 *Capital One* — `"""+spoofing_numbers[12]+"""`
🏦 *Td Bank* — `"""+spoofing_numbers[13]+"""`
🏦 *Hsbc Bank Usa* — `"""+spoofing_numbers[14]+"""`
🏦 *Usaa* — `"""+spoofing_numbers[15]+"""`
💳 *American Express* — `"""+spoofing_numbers[16]+"""`
🏦 *Charles Schwab* — `"""+spoofing_numbers[17]+"""`
🛋 *Ikea* — `"""+spoofing_numbers[18]+"""`
🛋 *Ashley Furniture* — `"""+spoofing_numbers[19]+"""`
🛍 *Wayfair* — `"""+spoofing_numbers[20]+"""`
🛏 *Slumberland Furniture* — `"""+spoofing_numbers[21]+"""`
📱 *Oneplus* — `"""+spoofing_numbers[22]+"""`
📱 *Sony Mobile* — `"""+spoofing_numbers[23]+"""`
📱 *Nokia* — `"""+spoofing_numbers[24]+"""`
📱 *Htc* — `"""+spoofing_numbers[25]+"""`
📱 *Blackberry* — `"""+spoofing_numbers[26]+"""`
🔎 *Google* — `"""+spoofing_numbers[27]+"""`
🚙 *Jeep* — `"""+spoofing_numbers[28]+"""`
💰 *paypal* — `"""+spoofing_numbers[29]+"""`
📲 *venmo* — `"""+spoofing_numbers[30]+"""`
🍎 *applepay* — `"""+spoofing_numbers[31]+"""`
💱 *coinbase* — `"""+spoofing_numbers[32]+"""`
📧 *microsoft* — `"""+spoofing_numbers[33]+"""`
📦 *amazon* — `"""+spoofing_numbers[34]+"""`
🛍 *quadpay* — `"""+spoofing_numbers[35]+"""`
💸 *cashapp* — `"""+spoofing_numbers[36]+"""`
🏛 *citizens* — `"""+spoofing_numbers[37]+"""`
👤 *marcus* — `"""+spoofing_numbers[38]+"""`
📲 *carrier* — `"""+spoofing_numbers[39]+"""`"""
    return msg
def get_crypto_price_amount(symbol, amount):
    temp = str(amount)+'$'
    coins = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'LTC': 'litecoin',
        'SOL': 'solana'
    }

    symbol = symbol.upper()
    if symbol not in coins:
        return temp


    coin_id = coins[symbol]
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': coin_id, 'vs_currencies': 'usd'}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return temp

    data = response.json().get(coin_id, {})
    usd_price = data.get('usd')

    if not isinstance(usd_price, (int, float)):
        return temp

    quantity = amount / usd_price
    return f"${amount} ≈ {quantity:.8f} {symbol}"

def escape_markdown(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!\\,"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def is_name_valid(name):
    test = name.isalpha()
    if name.upper() in spoofing_services:
        test = 'Found'
    return test


def duration(duration_code):
    if duration_code == '2HOUR':
        duration = '2Hours'
    elif duration_code == '1DAYZ':
        duration = '1Day'
    elif duration_code == '3DAYZ':
        duration = '3Days'
    elif duration_code == '1WEEK':
        duration = '1Week'
    elif duration_code == '1MNTH':
        duration = '1Month'
    return duration


def check_subscription(Expiry_Date):
    if Expiry_Date == 'N/A':
        return 'Null'
    now = datetime.now()
    expire_date = datetime.strptime(str(Expiry_Date), "%Y-%m-%d %H:%M:%S.%f")
    if expire_date > now:
        return True
    else:
        return False

def is_valid_phone_number(number: str, region: str = None) -> bool:
    try:
        parsed_number = phonenumbers.parse(number, region)
        return phonenumbers.is_valid_number(parsed_number)
    except NumberParseException:
        return False
    
def check_spoof(spoof_number,service_name,name,list):
    if name.upper() in spoofing_services:
        return 'Name Found'
    spoof_place = 'N/A'
    try:
        spoof_place = list.index(spoof_number)
    except ValueError:
        try:
            if vip_spoof.index(spoof_number):
                spoof_place = 'VIP'
        except ValueError:
            return 'Not Found'
    try:
        service_place = spoofing_services.index(service_name.upper())
    except ValueError:
        if spoof_place == 'VIP':
            return True
        else:
            return 'Found'
    if spoof_place == service_place:
        return True
    else:
        return False

def get_spoof_number(service_name):
    service_place = spoofing_services.index(service_name.upper())
    return spoofing_numbers[service_place]

def get_service_name(service_name):
    try:
        service_place = spoofing_services.index(service_name.upper())
        return services[service_place]
    except ValueError:
        return service_name
    
def get_service_name_bynum(num):
    service_place = spoofing_numbers.index(num)
    return services[service_place]

def check_otp_len(otp):
    if otp.isdigit() == False:
        return 'Null'
    if 4<=int(otp)<=8:
        return True
    else:
        return False

def get_wallet_message(sym,amm):
    now = str(datetime.now())
    payment_time = now[0:16]
    symbole = sym.upper()
    if amm == 20:
        plan = '`Spoof Number`'
    elif amm == 30:
        plan = '`1 Day Plan`'
    elif amm == 55:
        plan = '`3 Days Plan`'
    elif amm == 95:
        plan = '`1 Week Plan`'
    elif amm == 210:
        plan = '`1 Month Plan`'
    if symbole == 'USDT':
        return """ℹ Payment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 *Currency*\: `USDT (trc20)`
💰 *Amount*\: `"""+str(amm)+"""$ ≈ """+str(amm)+""" USDT`
📅 *Date*\: `"""+str(escape_markdown(payment_time))+"""`
⏳ *Plan*\: """+plan+"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 *Wallet*\: `TRRVAuPEGJ4EgE33u1pV6gNUXxM1R5v1aY`

🔐 *To complete your purchase*\:
Send the amount via the *USDT* wallet and send a screenshot to Support\."""
    elif symbole == 'BTC':
        return """ℹ Payment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 *Currency*\: `"""+symbole+""" (SegWit)`
💰 *Amount*\: `"""+(get_crypto_price_amount(symbole,amm))+""")`
📅 *Date*\: `"""+str(escape_markdown(payment_time))+"""`
⏳ *Plan*\: """+plan+"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 *Wallet*\: `bc1q98y83fh28y6ysklu9qmla7enuegldmgdcdawvk`

🔐 *To complete your purchase*\:
Send the amount via the *"""+symbole+"""* wallet and send a screenshot to Support\."""
    elif symbole == 'ETH':
        return """ℹ Payment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 *Currency*\: `"""+symbole+""" (ERC20)`
💰 *Amount*\: `"""+(get_crypto_price_amount(symbole,amm))+""")`
📅 *Date*\: `"""+str(escape_markdown(payment_time))+"""`
⏳ *Plan*\: """+plan+"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 *Wallet*\: `0xc76acc06684b2e2a2d43b9ba3b5f2618cd7a6307`

🔐 *To complete your purchase*\:
Send the amount via the *"""+symbole+"""* wallet and send a screenshot to Support\."""
    elif symbole == 'SOL':
        return """ℹ Payment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 *Currency*\: `"""+symbole+""" (SOLANA)`
💰 *Amount*\: `"""+(get_crypto_price_amount(symbole,amm))+""")`
📅 *Date*\: `"""+str(escape_markdown(payment_time))+"""`
⏳ *Plan*\: """+plan+"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 *Wallet*\: `8Ra9HKVrKNakEeQfqDzrVn1sFoQoFmbR51UHMRweT9hY`

🔐 *To complete your purchase*\:
Send the amount via the *"""+symbole+"""* wallet and send a screenshot to Support\."""
    elif symbole == 'ETH':
        return """ℹ Payment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 *Currency*\: `"""+symbole+""" (ERC20)`
💰 *Amount*\: `"""+(get_crypto_price_amount(symbole,amm))+""")`
📅 *Date*\: `"""+str(escape_markdown(payment_time))+"""`
⏳ *Plan*\: """+plan+"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 *Wallet*\: `0xc76acc06684b2e2a2d43b9ba3b5f2618cd7a6307`

🔐 *To complete your purchase*\:
Send the amount via the *"""+symbole+"""* wallet and send a screenshot to Support\."""
    elif symbole == 'LTC':
        return """ℹ Payment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 *Currency*\: `"""+symbole+""" (LITECOIN)`
💰 *Amount*\: `"""+(get_crypto_price_amount(symbole,amm))+""")`
📅 *Date*\: `"""+str(escape_markdown(payment_time))+"""`
⏳ *Plan*\: """+plan+"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 *Wallet*\: `LRJ8n55djedy4jyKP3Kkqi6iEy3BYC1FLt`

🔐 To complete your purchase\:
Send the amount via the *"""+symbole+"""* wallet and send a screenshot to Support\."""