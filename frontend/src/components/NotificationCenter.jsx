import { useState, useEffect } from 'react';
import { Bell, X, Check, Calendar, Zap, Info } from 'lucide-react';
import api from '../services/api';

const NotificationCenter = () => {
    const [notifications, setNotifications] = useState([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const response = await api.get('/notifications/');
                setNotifications(response.data);
                setUnreadCount(response.data.filter(n => !n.is_read).length);
            } catch (err) {
                console.error("Failed to fetch notifications");
            }
        };

        fetchNotifications();
        const interval = setInterval(fetchNotifications, 10000); // Poll every 10 seconds
        return () => clearInterval(interval);
    }, []);

    const markAsRead = async (id) => {
        try {
            await api.patch(`/notifications/${id}/read`);
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
            setUnreadCount(prev => Math.max(0, prev - 1));
        } catch (err) {
            console.error("Failed to mark notification as read");
        }
    };

    const deleteNotification = async (id, e) => {
        e.stopPropagation();
        try {
            await api.delete(`/notifications/${id}`);
            setNotifications(prev => prev.filter(n => n.id !== id));
            if (!notifications.find(n => n.id === id).is_read) {
                setUnreadCount(prev => Math.max(0, prev - 1));
            }
        } catch (err) {
            console.error("Failed to delete notification");
        }
    };

    const getTypeIcon = (type) => {
        switch (type) {
            case 'daily_task': return <Calendar className="w-4 h-4 text-emerald-400" />;
            case 'reminder': return <Zap className="w-4 h-4 text-indigo-400" />;
            default: return <Info className="w-4 h-4 text-blue-400" />;
        }
    };

    return (
        <div className="relative">
            <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="relative p-2 rounded-xl glass-button text-slate-400 hover:text-white transition-all shadow-lg"
            >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white shadow-glow">
                        {unreadCount}
                    </span>
                )}
            </button>

            {showDropdown && (
                <div className="absolute right-0 mt-4 w-80 bg-slate-900 border border-white/10 rounded-3xl shadow-2xl z-50 overflow-hidden animate-in slide-in-from-top-2 duration-200">
                    <div className="p-4 border-b border-white/5 bg-white/5 flex justify-between items-center">
                        <h3 className="font-bold text-white text-sm">Notifications</h3>
                        <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                            {unreadCount} New
                        </span>
                    </div>

                    <div className="max-h-96 overflow-y-auto">
                        {notifications.length === 0 ? (
                            <div className="p-8 text-center text-slate-500 text-sm">
                                All caught up!
                            </div>
                        ) : (
                            notifications.map(note => (
                                <div
                                    key={note.id}
                                    onClick={() => !note.is_read && markAsRead(note.id)}
                                    className={`p-4 border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer relative group ${!note.is_read ? 'bg-indigo-500/5' : ''}`}
                                >
                                    <div className="flex space-x-3">
                                        <div className="mt-1 p-2 rounded-lg bg-white/5">
                                            {getTypeIcon(note.type)}
                                        </div>
                                        <div className="flex-1 space-y-1">
                                            <p className={`text-sm font-bold ${!note.is_read ? 'text-white' : 'text-slate-400'}`}>
                                                {note.title}
                                            </p>
                                            <p className="text-xs text-slate-500 leading-relaxed">
                                                {note.message}
                                            </p>
                                            <p className="text-[8px] uppercase font-bold text-slate-600">
                                                {new Date(note.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => deleteNotification(note.id, e)}
                                        className="absolute top-4 right-4 p-1 rounded-md opacity-0 group-hover:opacity-100 hover:bg-white/10 text-slate-500 transition-all"
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationCenter;
