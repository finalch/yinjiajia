import base64
from flask import jsonify


def validate(token):
    try:
        raw = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        parts = raw.split(':')
        if len(parts) != 3:
            return False
        merchant_id = int(parts[0])
        epoch_ms = int(parts[1])
        rand_suffix = int(parts[2])
        return merchant_id
    except Exception as e:
        print("Error parsing token:", e)
        return False
