import requests


def python_request(method, url, **kwargs):
    return requests.request(method, url, **kwargs)