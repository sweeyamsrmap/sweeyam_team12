import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';

import Calendar from './pages/Calendar';
import Profile from './pages/Profile';

import { ToastProvider } from './components/ToastProvider';

function App() {
  return (
    <Router>
      <ToastProvider>
        <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-purple-500/30 selection:text-purple-200">
          {/* Abstract Background Orbs */}
          <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/20 rounded-full blur-[120px]" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/20 rounded-full blur-[120px]" />
          </div>

          <Navbar />
          <main className="container mx-auto px-4 py-8 relative z-10">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/calendar" element={<Calendar />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </main>
        </div>
      </ToastProvider>
    </Router>
  );
}

export default App;
