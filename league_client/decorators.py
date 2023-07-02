import json

import requests


def handle_excpetions(default=True):
    def decorator(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (json.decoder.JSONDecodeError, requests.RequestException):
                return default

        return inner

    return decorator
