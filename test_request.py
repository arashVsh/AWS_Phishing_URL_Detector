#!/usr/bin/env python
"""
test_request.py

Usage:
  py test_request.py                      # uses default http://127.0.0.1:5000
  py test_request.py --url https://<env>  # point to your EB URL

Requirements:
  pip install requests
"""
import argparse
import requests
import json
import sys
from pprint import pprint

DEFAULT_BASE = "http://127.0.0.1:5000"
TIMEOUT = 15

def pretty(resp):
    try:
        return json.dumps(resp, indent=2)
    except Exception:
        return str(resp)

def health(base):
    url = f"{base.rstrip('/')}/"
    print(f"\n[HEALTH] GET {url}")
    try:
        r = requests.get(url, timeout=TIMEOUT)
        print("Status:", r.status_code)
        try:
            print(pretty(r.json()))
        except Exception:
            print(r.text[:1000])
    except Exception as e:
        print("Error:", e)

def single_url(base, url_to_test):
    url = f"{base.rstrip('/')}/predict_url"
    payload = {"url": url_to_test}
    print(f"\n[SINGLE URL] POST {url}\nPayload: {payload}")
    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        print("Status:", r.status_code)
        print(pretty(r.json()))
    except Exception as e:
        print("Error:", e)
        try:
            print("Raw response:", r.text)
        except:
            pass

def batch_urls(base, urls):
    url = f"{base.rstrip('/')}/predict_url"
    payload = [{"url": u} for u in urls]
    print(f"\n[BATCH URLS] POST {url}\nPayload:", payload)
    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        print("Status:", r.status_code)
        print(pretty(r.json()))
    except Exception as e:
        print("Error:", e)
        try:
            print("Raw response:", r.text)
        except:
            pass

def predict_features(base, feature_dict_or_list):
    url = f"{base.rstrip('/')}/predict"
    payload = feature_dict_or_list
    print(f"\n[PREDICT FEATURES] POST {url}\nPayload:")
    pprint(payload)
    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        print("Status:", r.status_code)
        print(pretty(r.json()))
    except Exception as e:
        print("Error:", e)
        try:
            print("Raw response:", r.text)
        except:
            pass

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", "-u", default=DEFAULT_BASE, help="Base URL of the running API (default: http://127.0.0.1:5000)")
    args = p.parse_args()
    base = args.url.rstrip('/')

    print("Running tests against:", base)

    # 1) Health
    health(base)

    # 2) Single URL test
    single_url(base, "http://free-gift-cards.win/login")

    # 3) Batch URLs
    batch_urls(base, [
        "http://free-gift-cards.win/login",
        "http://example.com",
        "https://login.microsoftonline.com/signin"
    ])

    # 4) Predict by feature dict (server will fill missing features with zeros)
    feature_sample = {
        "url_len": 45,
        "num_digits": 4,
        "num_dots": 3,
        "has_https": 0,
        "has_at": 0,
        "has_ip": 0,
        "has_hyphen": 1,
        "has_query": 0,
        "num_slashes": 3
    }
    predict_features(base, feature_sample)

    # 5) Predict by feature list (two entries)
    feature_list = [
        feature_sample,
        {"url_len": 12, "num_digits": 0, "num_dots": 1}
    ]
    predict_features(base, feature_list)

    print("\nDone.")

if __name__ == "__main__":
    main()
