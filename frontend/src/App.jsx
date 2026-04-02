import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import SignalFeed from './pages/SignalFeed';
import WhiteWhales from './pages/WhiteWhales';
import ActionQueue from './pages/ActionQueue';
import PromptStudio from './pages/PromptStudio';
import Settings from './pages/Settings';
import Admin from './pages/Admin';
import './index.css';

function ProtectedLayout() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <p className="text-gray-500 text-sm">loading...</p>
      </div>
    );
  }

  if (!user) return <Navigate to="/login" />;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-950">
        <Routes>
          <Route path="/" element={<SignalFeed />} />
          <Route path="/whales" element={<WhiteWhales />} />
          <Route path="/actions" element={<ActionQueue />} />
          <Route path="/prompts" element={<PromptStudio />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<ProtectedLayout />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
