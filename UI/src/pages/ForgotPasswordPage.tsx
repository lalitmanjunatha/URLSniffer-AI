import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth/auth';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const { resetPassword } = useAuth();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setError('Please enter email');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await resetPassword(email);
      setSuccess(true);
    } catch (err: any) {
      const msg = err?.message?.replace(/.*?:\s*/, '') || 'Failed to send reset link';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="w-full max-w-md space-y-6">
        <h2 className="text-2xl font-bold text-center">Forgot password</h2>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}
          {success && (
            <p className="text-sm text-green-600">
              If an account exists with that email, you will receive a reset link.
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:offset-2 focus-visible:outline-indigo-600"
          >
            {loading ? 'Sending…' : 'Send reset link'}
          </button>
          <p className="text-center text-sm text-gray-500">
            <a href="/login" className="font-medium text-indigo-600 hover:underline">Back to Sign in</a>
          </p>
        </form>
      </div>
    </div>
  );
}