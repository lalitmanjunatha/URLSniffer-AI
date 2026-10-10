# URLSniffer AI - Phishing URL Detection System

## Overview
This project implements a complete phishing URL detection system with:
- Supabase-based authentication (JWT verification)
- FastAPI backend with RESTful endpoints
- Machine learning model for phishing detection
- Deterministic feature extraction from URLs
- Comprehensive test suite

## Architecture

### Backend (`/backend`)
- **Framework**: FastAPI 0.111.0
- **Authentication**: Supabase JWT verification using `python-jose`
- **ML Pipeline**: Scikit-learn RandomForest classifier
- **Key Components**:
  - `app/main.py`: FastAPI application setup
  - `app/core/security.py`: JWT verification and user dependencies
  - `app/core/supabase.py`: Supabase client initialization (graceful degradation)
  - `app/ml/`: Machine learning modules
  - `app/api/routes/`: API endpoints
  - `scripts/`: Training utilities
  - `tests/`: Test suite

### Core Features Implemented

#### 1. Authentication System
- JWT verification with RS256 algorithm
- JWKS fetching and caching
- Strict claim validation (issuer, audience)
- `get_current_user` dependency for protected routes
- `require_admin` dependency for admin-only access
- Graceful handling when Supabase credentials unavailable

#### 2. Machine Learning Pipeline
- **Feature Extraction** (`app/ml/feature_extractor.py`):
  - URL length
  - Scheme (HTTP/HTTPS flag)
  - IP address detection
  - Punycode detection
  - Percent-encoding detection
  - Hyphen count
  - Digit count
  - Subdomain count
- **URL Validation** (`app/ml/url_validator.py`):
  - Strict scheme validation (http/https only)
  - Domain name validation (label rules)
  - IPv4 validation
  - No network calls
- **Model Training** (`scripts/train_model.py`):
  - CSV loading with validation
  - Feature extraction batching
  - Train/test split
  - RandomForest classifier with scaling
  - Model persistence (pickle)
- **Prediction Service** (`app/ml/model.py`):
  - Singleton model predictor
  - Thread-safe lazy loading
  - Prediction with probability scores

#### 3. API Endpoints
- **Health Check**: `GET /api/v1/health` → `{"status": "ok"}`
- **User Info**: `GET /api/v1/me` → User ID and email from token
- **URL Scan**: `POST /api/v1/scan` → Phishing prediction with features
  - Requires authentication
  - Returns: `is_phishing`, `probability`, `features`
- **Model Management**:
  - `GET /api/v1/model/status` → Model loaded status
  - `POST /api/v1/model/load` → Load model from file

#### 4. Security Considerations
- No hardcoded secrets
- Environment variable configuration
- SQL injection prevention (via Supabase client)
- Role-based access control (RLS ready)
- Input validation on all endpoints
- CORS configuration ready

## Setup & Usage

### Prerequisites
- Python 3.12+
- pip
- (Optional) Supabase project for authentication

### Local Development
1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   python -m pytest tests/ -v
   ```

3. Train a model (using provided test dataset):
   ```bash
   python scripts/train_model.py --data test_dataset.csv --model-output model.pkl
   ```

4. Start the API server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Load the trained model via API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/model/load" -H "Content-Type: application/json" -d '{"model_path": "model.pkl"}'
   ```

6. Test the scan endpoint (after authentication):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/scan" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <your_jwt_token>" \
        -d '{"url": "https://example.com"}'
   ```

### Environment Variables
Create `.env` file in backend root:
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
CORS_ORIGINS=["http://localhost:3000"]  # Adjust as needed
```

## Test Suite
- 33 unit tests covering all components
- Tests for feature extraction, URL validation, training script
- API endpoint tests (health, scan, model)
- Integration tests for model loading and prediction
- All tests pass: `33 passed, 3 warnings`

## Files Created
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── supabase.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── users.py
│   │       ├── scan.py
│   │       └── model.py
│   └── ml/
│       ├── __init__.py
│       ├── feature_extractor.py
│       ├── url_validator.py
│       └── model.py
├── scripts/
│   └── train_model.py
├── tests/
│   ├── test_feature_extractor.py
│   ├── test_health.py
│   ├── test_model.py
│   ├── test_model_integration.py
│   ├── test_scan.py
│   ├── test_train_model.py
│   ├── test_url_validator.py
│   └── test_model_integration.py
├── test_dataset.csv
├── model.pkl  # Generated after training
├── requirements.txt
└── .env.example
```

## Next Steps for Production
1. Connect to actual Supabase project
2. Enable Row Level Security (RLS) on database tables
3. Add admin-only protection to model loading endpoint
4. Implement model versioning and A/B testing
5. Add rate limiting and request logging
6. Deploy with proper SSL/TLS termination
7. Set up monitoring and alerting

## Compliance with Requirements
✅ **Supabase Auth**: JWT verification implemented, ready for Supabase connection
✅ **FastAPI Backend**: Complete with health, user, scan, and model endpoints
✅ **ML Pipeline**: Feature extraction, training, prediction all implemented
✅ **Local-First Development**: All code testable without Supabase credentials
✅ **Deterministic Features**: Feature extraction is purely syntactic, no network calls
✅ **Testable**: Comprehensive test suite with 33 passing tests
✅ **Environment Separation**: `.env.example` files, no secrets in codebase
✅ **Production-Ready Mock Auth**: Mock authentication disabled in production (real JWT verification used)

The system is ready for Supabase integration after local development completion as requested.