# app.py
from flask import Flask, request, jsonify
import os
import io
import joblib
import pandas as pd
import re
import traceback
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Put this near the top of app.py (replace your current load_model_bundle)
import requests

MODEL_LOCAL = "phish_model_bundle.pkl"
# Prefer env var; fall back to a hardcoded public URL only if you want:
MODEL_S3_URI = os.environ.get("MODEL_S3_URI",
    "https://my-phish-model-arash-2025.s3.us-east-2.amazonaws.com/phish_model_bundle.pkl"
)

def load_model_bundle():
    """Load model from local file, an s3:// URI, or an https:// URL."""
    # 1) Local file (developer convenience)
    if os.path.exists(MODEL_LOCAL):
        print("✅ Loading model locally:", MODEL_LOCAL)
        return joblib.load(MODEL_LOCAL)

    # 2) s3:// — use boto3 (requires IAM permission on EB instance or aws creds locally)
    if MODEL_S3_URI and MODEL_S3_URI.startswith("s3://"):
        print("⬇️  Downloading model from S3:", MODEL_S3_URI)
        s3 = boto3.client("s3")
        _, _, path = MODEL_S3_URI.partition("s3://")
        bucket, _, key = path.partition("/")
        buf = io.BytesIO()
        try:
            s3.download_fileobj(bucket, key, buf)
            buf.seek(0)
            return joblib.load(buf)
        except (BotoCoreError, ClientError) as e:
            print("❌ S3 download failed:", e)
            raise

    # 3) https:// or http:// — use requests (works for public objects or presigned URLs)
    if MODEL_S3_URI and (MODEL_S3_URI.startswith("https://") or MODEL_S3_URI.startswith("http://")):
        print("⬇️  Downloading model from HTTP(S):", MODEL_S3_URI)
        try:
            resp = requests.get(MODEL_S3_URI, timeout=30)
            resp.raise_for_status()
            buf = io.BytesIO(resp.content)
            buf.seek(0)
            return joblib.load(buf)
        except Exception as e:
            print("❌ HTTP(S) download failed:", e)
            raise

    raise FileNotFoundError("Model not found locally and MODEL_S3_URI not set to s3:// or http(s)://")


app = Flask(__name__)

# --- load model bundle ---
try:
    bundle = load_model_bundle()
    model = bundle["model"]
    imputer = bundle["imputer"]
    feature_cols = bundle["feature_cols"]
    print("Model bundle loaded. Feature cols:", len(feature_cols))
except Exception as e:
    print("ERROR loading model bundle:", e)
    model = None
    imputer = None
    feature_cols = []

# --- routes ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Phishing Detector API running", "endpoints": ["/predict", "/predict_url"]})

def simple_url_features(url):
    u = str(url)
    return {
        'url_len': len(u),
        'num_digits': sum(c.isdigit() for c in u),
        'num_dots': u.count('.'),
        'has_https': int('https' in u.lower()),
        'has_at': int('@' in u),
        'has_ip': int(bool(re.search(r'\d+\.\d+\.\d+\.\d+', u))),
        'has_hyphen': int('-' in u),
        'has_query': int('?' in u),
        'num_slashes': u.count('/'),
    }

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        if isinstance(data, dict):
            X = pd.DataFrame([data])
        elif isinstance(data, list):
            X = pd.DataFrame(data)
        else:
            return jsonify({"error": "Payload must be a dict or list of dicts"}), 400

        # ensure required feature columns present
        missing = [c for c in feature_cols if c not in X.columns]
        for m in missing:
            X[m] = 0
        X = X[feature_cols]

        X_imp = pd.DataFrame(imputer.transform(X), columns=feature_cols)
        preds = model.predict(X_imp)
        probs = model.predict_proba(X_imp)[:, 1] if hasattr(model, "predict_proba") else [None]*len(preds)

        out = []
        for p, pr in zip(preds, probs):
            out.append({"prediction": int(p), "label": "phishing" if int(p) == 1 else "legitimate",
                        "confidence": float(pr) if pr is not None else None})
        return jsonify(out)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/predict_url", methods=["POST"])
def predict_url():
    try:
        payload = request.get_json(force=True)
        # normalize to list of dicts with 'url' key
        inputs = []
        if isinstance(payload, dict) and 'url' in payload:
            inputs = [payload]
        elif isinstance(payload, list):
            inputs = payload
        else:
            return jsonify({"error": "JSON must be {'url':'...'} or a list of such dicts"}), 400

        rows = []
        for item in inputs:
            url = item.get('url', '')
            rows.append(simple_url_features(url))

        X = pd.DataFrame(rows)

        # fill any missing model feature columns with zeros
        for col in feature_cols:
            if col not in X.columns:
                X[col] = 0

        X = X[feature_cols]
        X_imp = pd.DataFrame(imputer.transform(X), columns=feature_cols)

        preds = model.predict(X_imp)
        probs = model.predict_proba(X_imp)[:, 1] if hasattr(model, "predict_proba") else [None]*len(preds)

        results = []
        for p, pr in zip(preds, probs):
            results.append({"prediction": int(p), "label": "phishing" if int(p) == 1 else "legitimate",
                            "confidence": float(pr) if pr is not None else None})
        return jsonify(results)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
