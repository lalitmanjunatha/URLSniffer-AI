# URLSniffer: AI-Powered Phishing Detection with Supabase Authentication

URLSniffer is a full-stack web application designed to detect phishing URLs using machine learning. It provides users with a secure interface to analyze URLs for phishing attempts, leveraging a trained AI model and Supabase for authentication and user management.

## 🚀 Features

- **AI-Powered Phishing Detection**: Utilizes a Random Forest classifier trained on the UCI PhiUSIIL Phishing URL Dataset to analyze URLs and predict phishing likelihood.
- **Secure Authentication**: Integrated with Supabase for user authentication, including email/password login, signup, password reset, and session management.
- **Protected Routes**: Frontend and backend routes are protected, requiring authentication for access to sensitive features.
- **Role-Based Access Control (RBAC)**: Supports user and admin roles, with admin-only routes protected by Supabase and database-backed role checks.
- **Rate Limiting**: Implements rate limiting on the scan endpoint to prevent abuse.
- **CORS Support**: Configurable CORS origins for development and production environments.
- **Environment Configuration**: Uses environment variables for easy configuration across different environments.
- **Responsive Design**: Built with React, Tailwind CSS, and Vite for a modern, responsive user interface.
- **Comprehensive Testing**: Includes unit tests for backend functionality and type-checking for frontend.

## 🏗️ Architecture

### Backend (`/backend`)
- **Framework**: FastAPI (Python)
- **Authentication**: Supabase JWT verification (RS256 via JWKS)
- **Machine Learning**: Scikit-learn Random Forest classifier with StandardScaler
- **Key Components**:
  - `app/main.py`: FastAPI application setup
  - `app/core/security.py`: Supabase JWT verification and authentication dependencies
  - `app/ml/model.py`: Model loading, prediction, and feature extraction utilities
  - `app/api/routes/`: API endpoints for health, user management, scanning, and model status
  - `app/ml/feature_extractor.py`: Deterministic feature extraction from URLs
  - `app/ml/url_validator.py`: Strict URL validation (syntax only)

### Frontend (`/UI`)
- **Framework**: React with Vite
- **Styling**: Tailwind CSS v4
- **State Management**: React Context API for authentication state
- **Routing**: React Router v7
- **Key Components**:
  - `src/lib/auth/auth.tsx`: Authentication context and Supabase client
  - `src/lib/auth/ProtectedRoute.tsx`: Route protection components (public, protected, admin-protected)
  - `src/AppRouter.tsx`: Application routing configuration
  - `src/lib/api/client.ts`: API client with automatic JWT attachment
  - `src/components/`: Reusable UI components (not detailed in this overview)

## ⚙️ Setup and Installation

### Prerequisites
- Node.js (v18+ recommended) and npm/pnpm
- Python (v3.10+ recommended)
- Git
- A Supabase account (for authentication backend)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
4. Configure the `.env` file with your Supabase credentials:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_ANON_KEY=your_supabase_anon_public_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   ```
   > **Note**: For development/testing, you can use placeholder values (e.g., `http://localhost` and `anon-key`), but authentication will not work without a valid Supabase project.

5. (Optional) Start the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup
1. Navigate to the UI directory:
   ```bash
   cd UI
   ```
2. Install JavaScript dependencies:
   ```bash
   npm install
   # or if you prefer pnpm
   pnpm install
   ```
3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
4. Configure the `.env` file with your Supabase and API URL:
   ```env
   VITE_SUPABASE_URL=your_supabase_project_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_public_key
   VITE_API_URL=http://localhost:8000/api/v1   # Adjust if your backend runs on a different URL
   ```
   > **Note**: For development with the placeholder backend, you can use:
   > ```env
   > VITE_SUPABASE_URL=http://localhost
   > VITE_SUPABASE_ANON_KEY=anon-key
   > VITE_API_URL=http://localhost:8000/api/v1
> ```

5. Start the frontend development server:
   ```bash
   npm run dev
   # or
   pnpm dev
   ```
   The application will be available at `http://localhost:8443`.

## 🛠️ Running the Project

### Option 1: Using Docker (Recommended for Production)
> Note: Docker setup is not included in this repository. You would need to create Dockerfiles for both backend and frontend and use docker-compose.

### Option 2: Manual Setup (Development)
1. Start the backend server (in one terminal):
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
2. Start the frontend server (in another terminal):
   ```bash
   cd UI
   npm run dev
   ```
3. Open your browser to `http://localhost:8443` to use the application.

### Option 3: Using the Provided Scripts
The project includes scripts for dataset download and model training (in the `backend/scripts` directory). These are for retraining the model and are not required to run the application with the pre-trained model.

## 🔐 Authentication Flow

1. **User Signup/Login**: Users can create an account or log in via email and password.
2. **JWT Issuance**: Upon successful authentication, Supabase issues a JSON Web Token (JWT).
3. **Token Storage**: The JWT is stored in memory (not in localStorage) via the Supabase client.
4. **API Requests**: The frontend automatically attaches the JWT to all API requests via the `src/lib/api/client.ts` module.
5. **Token Verification**: The backend verifies the JWT using Supabase's JWKS (JSON Web Key Set) and the RS256 algorithm.
6. **Protected Routes**: Both frontend routes (via `ProtectedRoute` components) and backend endpoints (via `get_current_user` dependency) check for a valid token.

## 📊 Model Information

The application uses a pre-trained Random Forest classifier (`model.pkl`) located in the backend directory. The model was trained on the UCI PhiUSIIL Phishing URL Dataset with the following characteristics:
- **Features**: 27 features extracted from URLs (including lexical, hostname, and content-based features)
- **Classes**: 0 (legitimate), 1 (phishing)
- **Performance** (on test set):
  - Accuracy: ~88%
  - ROC-AUC: ~0.9345
  - Precision: ~0.83 (legitimate), ~0.96 (phishing)
  - Recall: ~0.98 (legitimate), ~0.74 (phishing)

## 🧪 Testing

### Backend Tests
Run the backend test suite:
```bash
cd backend
pytest
```
All 33 tests should pass.

### Frontend Checks
- TypeScript compilation: `npm run tsc` (or check for errors during `npm run dev`)
- Linting: Not currently configured, but the code follows standard React/TypeScript practices.

## 📁 Project Structure

```
URLSniffer/
├── backend/                    # Python/FastAPI backend
│   ├── app/
│   │   ├── api/                # API routes
│   │   │   ├── routes/         # Health, user, scan, model endpoints
│   │   ├── core/               # Configuration, security, Supabase client
│   │   ├── ml/                 # Machine learning model and utilities
│   │   │   ├── feature_extractor.py
│   │   │   ├── model.py
│   │   │   └── url_validator.py
│   │   └── main.py             # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── scripts/                # Dataset download and model training scripts
│   └── tests/                  # Backend unit tests
├── UI/                         # React/Vite frontend
│   ├── src/
│   │   ├── api/                # API client
│   │   ├── components/         # Reusable UI components
│   │   ├── lib/                # Authentication and utility libraries
│   │   │   ├── auth/           # Auth context and Supabase client
│   │   │   └── ProtectedRoute.tsx
│   │   ├── AppRouter.tsx       # Application routing
│   │   ├── main.tsx            # React entry point
│   │   └── index.css           # Global styles (Tailwind)
│   ├── index.html              # HTML template
│   ├── package.json            # Frontend dependencies and scripts
│   ├── tsconfig.json           # TypeScript configuration
│   └── vite.config.ts          # Vite configuration
├── README.md                   # This file
├── .env.example                # Example environment variables
├── SUPABASE_AUTH_FINAL_REPORT.md # Detailed report on Supabase integration
└── ...                         # Other documentation and reports
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure tests pass.
4. Submit a pull request with a clear description of your changes.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- The UCI PhiUSIIL Phishing URL Dataset for providing the training data.
- Supabase for providing an excellent authentication and backend-as-a-service platform.
- The open-source community for the various libraries and frameworks used.

---

**Get started now**: 
1. Clone the repository
2. Follow the setup instructions above
3. Visit http://localhost:8443 to analyze URLs for phishing attempts!
