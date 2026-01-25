import React, { useState, useEffect, createContext, useContext } from 'react';
import { X, Bell, Zap, CheckCircle, Info } from 'lucide-react';

const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const addToast = (title, message, type = 'info') => {
        const id = Math.random().toString(36).substr(2, 9);
        setToasts(prev => [...prev, { id, title, message, type }]);
        setTimeout(() => removeToast(id), 5000); // Auto-remove after 5s
    };

    const removeToast = (id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    };

    return (
        <ToastContext.Provider value={{ addToast }}>
            {children}
            <div className="fixed bottom-8 right-8 z-[100] flex flex-col space-y-4">
                {toasts.map(toast => (
                    <div
                        key={toast.id}
                        className="bg-slate-900 border border-white/10 p-6 rounded-[2rem] shadow-2xl flex items-start space-x-4 min-w-[320px] max-w-md animate-in slide-in-from-right-8 duration-300 relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 blur-[50px] -z-10"></div>
                        <div className={`p-3 rounded-2xl bg-white/5 ${toast.type === 'success' ? 'text-emerald-400' :
                                toast.type === 'alert' ? 'text-indigo-400' : 'text-blue-400'
                            }`}>
                            {toast.type === 'success' ? <CheckCircle className="w-6 h-6" /> :
                                toast.type === 'alert' ? <Zap className="w-6 h-6" /> : <Info className="w-6 h-6" />}
                        </div>
                        <div className="flex-1 space-y-1 pr-6">
                            <h4 className="text-white font-bold">{toast.title}</h4>
                            <p className="text-sm text-slate-400 leading-relaxed font-medium">{toast.message}</p>
                        </div>
                        <button
                            onClick={() => removeToast(toast.id)}
                            className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
};

export const useToast = () => useContext(ToastContext);
