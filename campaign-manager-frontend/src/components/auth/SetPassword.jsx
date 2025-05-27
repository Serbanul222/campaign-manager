import React, { useState } from 'react';
import useAuth from '../../hooks/useAuth.js';

const SetPassword = ({ token }) => {
  const { setPassword } = useAuth();
  const [password, setPwd] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    try {
      await setPassword(token, password);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to set password');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="text-red-600">{error}</p>}
      <input
        type="password"
        value={password}
        onChange={(e) => setPwd(e.target.value)}
        placeholder="New password"
        required
      />
      <input
        type="password"
        value={confirm}
        onChange={(e) => setConfirm(e.target.value)}
        placeholder="Confirm password"
        required
      />
      <button type="submit">Set Password</button>
    </form>
  );
};

export default SetPassword;
