
import os
from dotenv import load_dotenv
import requests
import string
import random


from django_otp.oath import TOTP
from .error_list import error_list

load_dotenv()

PHONNUMBER = os.getenv('PhoneNumber')
ACCESSHASH = os.getenv('AccessHash')
PATTERNID = os.getenv('PatternId')
URL = os.getenv('URL')

def to_roman_numeral(value):
    roman_map = {
        1: "I", 5: "V",
        10: "X", 50: "L",
        100: "C", 500: "D",
        1000: "M",
    }
    result = ""
    remainder = value

    for i in sorted(roman_map.keys(), reverse=True):
        if remainder > 0:
            multiplier = i
            roman_digit = roman_map[i]

            times = remainder // multiplier
            remainder = remainder % multiplier
            result += roman_digit * times

    return result


def message_error(status, code, error_code=None, data=None):
    data = data if data else error_list[error_code]
    result = {
        'data': data,
        'status': status,
        'code': code
    }
    return result

def send_sms(message, phone_number):
    params = {
        'AccessHash': ACCESSHASH,
        'PhoneNumber': PHONNUMBER,
        'PatternId': PATTERNID,
        'RecNumber': phone_number,
        'Smsclass': 1,
        'token1': message
    }
    try:
        response = requests.get(url=URL, params=params)
    except:
        return 500
    return response.status_code


ExTime = 120

def create_otp(user, model):
    device = model.objects.create(user=user, step=ExTime)
    device.save()
    totp = TOTP(key=device.bin_key, step=ExTime)
    token = totp.token()
    return token, device





def generate_password(length=12, include_special_chars=True):
    characters = string.ascii_letters + string.digits
    if include_special_chars:
        characters += string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password