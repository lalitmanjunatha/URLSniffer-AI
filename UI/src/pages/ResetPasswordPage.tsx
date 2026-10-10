import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth/auth';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const { updatePassword } = useAuth();
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password || !confirm) {
      setError('Please enter password and confirmation');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await updatePassword(password);
      setSuccess(true);
      // Optionally navigate after success
      setTimeout(() => navigate('/login'), 1500);
    } catch (err: any) {
      const msg = err?.message?.replace(/.*?:\s*/, '') || 'Failed to reset password';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="w-full max-w-md space-y-6">
        <h2 className="text-2xl font-bold text-center">Reset password</h2>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              New password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700">
              Confirm password
            </label>
            <input
              id="confirm_password"
              type="password"
              required
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}
          {success && (
            <p className="text-sm text-green-600">
              Password reset successful. You will be redirected to sign in.
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:offset-2 focus-visible:outline-indigo-600"
          >
            {loading ? 'Resetting…' : 'Reset Password'}
          </button>
          <p className="text-center text-sm text-gray-500">
            <a href="/login" className="font-medium text-indigo-600 hover:underline">Back to Sign in</a>
          </p>
        </form>
      </div>
    </div>
  );
}