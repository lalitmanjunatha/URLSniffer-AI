# Supabase Authentication Implementation Plan for URLSniffer

## Phase 1: Audit Findings

### Backend
- ✅ JWT verification logic exists in `backend/app/core/security.py`
- ✅ Uses JWKS approach for RS256 verification (correct for Supabase)
- ✅ `get_current_user` dependency extracts user_id and email from token
- ✅ `/api/v1/users/me` endpoint returns user info
- ❌ Config has conflicting JWT settings (SECRET_KEY/ALGORITHM=HS256) - not used
- ❌ Missing environment variable validation
- ❌ No role-based access control beyond basic authentication

### Frontend
- ✅ Supabase client initialized in `UI/src/lib/supabase.ts`
- ✅ Auth context with signup, login, logout, reset password flows
- ✅ ProtectedRoute component for route protection
- ✅ All pages wrapped in ProtectedRoute in AppRouter
- ✅ Login/Signup/Forgot/Reset pages exist
- ❌ AuthProvider creates profile on every auth state change (should be once)
- ❌ No handling of email confirmation flows
- ❌ No token refresh/expiration handling in API calls
- ❌ Missing role/admin checks in ProtectedRoute

### Database
- ✅ Profiles table exists with RLS policies
- ✅ Proper foreign key to auth.users
- ✅ Role column with check constraint
- ❌ Missing automatic profile creation on signup (handled in frontend)

## Phase 2: Implementation Steps

### Backend Fixes
1. Remove conflicting JWT config (SECRET_KEY, ALGORITHM) from config.py and .env.example
2. Add environment variable validation in config.py
3. Enhance security.py to handle missing Supabase configuration gracefully
4. Add role-based dependency for admin routes
5. Add middleware to attach user info to request for logging

### Frontend Fixes
1. Improve AuthProvider to:
   - Only create profile on initial signup (not every auth state change)
   - Handle email confirmation flows properly
   - Add loading states for auth operations
   - Clear error states appropriately
2. Enhance ProtectedRoute to:
   - Check for admin role when needed
   - Redirect authenticated users away from login/signup pages
   - Preserve intended destination after login
3. Update API client to automatically attach Authorization header
4. Add token refresh handling for expired sessions
5. Implement proper redirect after email verification

### Security Enhancements
1. Ensure no service keys are exposed to frontend
2. Validate that all API endpoints properly require authentication
3. Add rate limiting consideration for auth endpoints
4. Ensure password reset flows are secure

### Testing
1. Add backend tests for auth middleware
2. Add frontend tests for auth flows (mocked)
3. Add end-to-end test scenarios
4. Ensure existing tests still pass

### Documentation
1. Update .env.example files with clear comments
2. Document which variables are public vs private
3. Add setup instructions for Supabase
4. Document auth flows and security considerations