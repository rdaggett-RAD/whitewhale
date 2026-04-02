import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      navigate('/');
    } catch {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <form onSubmit={handleSubmit} className="w-80 space-y-4">
        <h1 className="text-2xl font-bold text-teal-400 tracking-tight text-center">
          WHITE WHALE
        </h1>
        <p className="text-xs text-gray-500 text-center">signal intelligence platform</p>

        {error && (
          <p className="text-red-400 text-xs text-center">{error}</p>
        )}

        <input
          type="email"
          placeholder="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded text-sm text-gray-200 focus:border-teal-500 focus:outline-none"
          required
        />
        <input
          type="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded text-sm text-gray-200 focus:border-teal-500 focus:outline-none"
          required
        />
        <button
          type="submit"
          className="w-full py-2 bg-teal-600 hover:bg-teal-500 text-white text-sm rounded transition-colors"
        >
          log in
        </button>
      </form>
    </div>
  );
}
