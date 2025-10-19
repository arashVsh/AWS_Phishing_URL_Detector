# Phishing URL Detector

A production-ready **phishing URL detection API** powered by machine learning and Flask, deployable both locally and on AWS Elastic Beanstalk.  
It classifies URLs as *phishing* or *legitimate* using handcrafted URL-based features.

---

## Features

- Machine learning model (RandomForest) trained on 58K+ URLs
- Real-time prediction via REST API
- Cloud-deployable on AWS Elastic Beanstalk
- Integrated testing script (`test_request.py`)
- Compatible with Python 3.10+  

---

## Project Structure

```
PhishingDetector/
│
├── app.py                  # Flask API (main application)
├── main.ipynb              # Model training and evaluation notebook
├── phish_model_bundle.pkl  # Trained model, imputer, and feature columns
├── requirements.txt        # Dependencies
├── Procfile                # Entry point for AWS deployment
├── test_request.py         # Test and benchmarking script
└── Utils.py                # Helper functions (e.g., visualization)
```

---

## 1. Run Locally

### **Setup**
```bash
git clone <your-repo-url>
cd PhishingDetector
python -m venv .venv
.venv\Scripts\activate   # On Windows
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### **Run the API**
```bash
python app.py
```

Visit:
```
http://127.0.0.1:5000/
```

Response:
```json
{"message": "Phishing Detector API running", "endpoints": ["/predict", "/predict_url"]}
```

---

## 2. Testing the API

### **Option 1 – cURL**
```bash
curl -X POST http://127.0.0.1:5000/predict_url      -H "Content-Type: application/json"      -d "{"url": "http://free-gift-cards.win/login"}"
```

### **Option 2 – Python Script**
```bash
python test_request.py
```

The script runs:
- Health check on `/`
- Single and batch URL predictions
- Raw feature-based prediction test

---

## 3. Deploy to AWS Elastic Beanstalk

### **Prerequisites**
- AWS account with access to Elastic Beanstalk and S3
- AWS CLI + EB CLI installed and configured:
  ```bash
  aws configure
  pip install awsebcli
  ```

### **Deployment Steps**
```bash
eb init -p python-3.13 PhishingDetector
eb create phish-detector-env --single --instance_type t3.micro
eb setenv MODEL_S3_URI="https://my-phish-model-arash-2025.s3.us-east-2.amazonaws.com/phish_model_bundle.pkl"
eb deploy
```

When environment is ready (`eb status` shows *Health: Green*), access:
```
https://phish-detector-env.eba-xxxxxxx.us-east-2.elasticbeanstalk.com/
```

---

## 4. Example API Endpoints

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/` | GET | Health check |
| `/predict_url` | POST | Predict phishing status from a raw URL |
| `/predict` | POST | Predict from pre-computed features |

Example `/predict_url` request:
```json
{"url": "https://login.microsoftonline.com/signin"}
```

Example response:
```json
[
  {
    "prediction": 0,
    "label": "legitimate",
    "confidence": 0.91
  }
]
```

---

## 5. Model File (`phish_model_bundle.pkl`)
This pickle contains:
- `model`: trained RandomForest classifier  
- `imputer`: feature imputer  
- `feature_cols`: list of features used during training  

It can be automatically downloaded from S3 if not found locally.

---

## 6. Troubleshooting

| Issue | Possible Cause | Solution |
|--------|----------------|-----------|
| Model not found | Missing or wrong S3 URL | Set `MODEL_S3_URI` correctly |
| Access denied | Bucket permissions restricted | Adjust IAM or bucket ACLs |
| Health = Red on EB | Missing dependencies or app crash | Run `eb logs` |
| JSONDecodeError in test script | Wrong endpoint or server error | Check `app.py` logs |

---

## License
This project is released for educational and development use.  
You are free to fork, adapt, or extend it under your own AWS account.

---

## Author
Developed by **Arash** — Graduate Researcher in Adversarial Machine Learning  
Focused on practical cloud-based ML deployment and real-world cybersecurity applications.
