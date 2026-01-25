import { Link, useNavigate } from 'react-router-dom';
import { LogOut, BookOpen, User as UserIcon, MessageSquare, Calendar as CalendarIcon } from 'lucide-react';

import NotificationCenter from './NotificationCenter';

const Navbar = () => {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <nav className="sticky top-0 z-50 backdrop-blur-xl bg-slate-950/70 border-b border-white/5 supports-[backdrop-filter]:bg-slate-950/50">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link to="/" className="flex items-center space-x-2 group">
                    <div className="bg-gradient-to-tr from-indigo-500 to-purple-500 p-2 rounded-lg group-hover:scale-105 transition-transform duration-300">
                        <BookOpen className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-display font-bold text-xl bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">QUBEX</span>
                </Link>

                <div className="flex items-center space-x-6">
                    {token ? (
                        <>
                            <NotificationCenter />
                            <Link to="/chat" className="text-slate-400 hover:text-white transition-colors flex items-center space-x-1.5 text-sm font-medium">
                                <MessageSquare className="w-4 h-4" />
                                <span>Chat</span>
                            </Link>
                            <Link to="/calendar" className="text-slate-400 hover:text-white transition-colors flex items-center space-x-1.5 text-sm font-medium">
                                <CalendarIcon className="w-4 h-4" />
                                <span>Schedule</span>
                            </Link>
                            <Link to="/profile" className="text-slate-400 hover:text-white transition-colors flex items-center space-x-1.5 text-sm font-medium">
                                <UserIcon className="w-4 h-4" />
                                <span>Profile</span>
                            </Link>
                            <Link to="/dashboard" className="text-slate-400 hover:text-white transition-colors flex items-center space-x-1.5 text-sm font-medium">
                                <UserIcon className="w-4 h-4" />
                                <span>Dashboard</span>
                            </Link>
                            <button onClick={handleLogout} className="text-slate-400 hover:text-red-400 transition-colors flex items-center space-x-1.5 text-sm font-medium">
                                <LogOut className="w-4 h-4" />
                                <span>Logout</span>
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="text-slate-400 hover:text-white transition-colors font-medium text-sm">Log In</Link>
                            <Link to="/register" className="bg-white text-slate-950 px-5 py-2 rounded-full font-medium text-sm hover:bg-slate-200 transition-all transform hover:scale-105 active:scale-95">
                                Get Started
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
