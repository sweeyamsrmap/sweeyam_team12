import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../services/api';
import { Send, User, Bot, Loader2, Plus, MessageSquare, Menu, MoreHorizontal, Pencil, Trash2 } from 'lucide-react';

const Chat = () => {
    const [sessions, setSessions] = useState([]);
    const [activeSessionId, setActiveSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [activeMenuId, setActiveMenuId] = useState(null);
    const [editingSessionId, setEditingSessionId] = useState(null);
    const [editTitle, setEditTitle] = useState('');
    const [status, setStatus] = useState('');
    const [searchParams] = useSearchParams();
    const [currentGoal, setCurrentGoal] = useState(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (activeMenuId && !event.target.closest('.group')) {
                setActiveMenuId(null);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [activeMenuId]);

    // Fetch sessions on mount
    useEffect(() => {
        fetchSessions();
        const sessionId = searchParams.get('sessionId');
        if (sessionId) {
            setActiveSessionId(parseInt(sessionId));
        }
    }, [searchParams]);

    const fetchSessions = async () => {
        try {
            const response = await api.get('/chat/sessions');
            setSessions(response.data);
            // Auto-selection removed: starts with a fresh chat state (null) by default
        } catch (err) {
            console.error("Failed to fetch sessions");
        }
    };

    const resetToNewChat = () => {
        setActiveSessionId(null);
        setMessages([]);
        setActiveMenuId(null);
    };

    const createNewSession = async () => {
        resetToNewChat();
    };

    const handleDeleteSession = async (sessionId, e) => {
        e.stopPropagation();
        if (!window.confirm("Delete this chat?")) return;
        try {
            await api.delete(`/chat/sessions/${sessionId}`);
            const updatedSessions = sessions.filter(s => s.id !== sessionId);
            setSessions(updatedSessions);
            if (activeSessionId === sessionId) {
                if (updatedSessions.length > 0) {
                    setActiveSessionId(updatedSessions[0].id);
                } else {
                    setActiveSessionId(null);
                    setMessages([]);
                }
            }
            setActiveMenuId(null);
        } catch (err) {
            console.error("Failed to delete session");
        }
    };

    const handleRenameSession = async (sessionId, e) => {
        e.stopPropagation();
        if (!editTitle.trim()) return;
        try {
            await api.patch(`/chat/sessions/${sessionId}`, { title: editTitle });
            setSessions(sessions.map(s => s.id === sessionId ? { ...s, title: editTitle } : s));
            setEditingSessionId(null);
        } catch (err) {
            console.error("Failed to rename session");
        }
    };

    const startEditing = (session, e) => {
        e.stopPropagation();
        setEditingSessionId(session.id);
        setEditTitle(session.title);
        setActiveMenuId(null);
    };

    // Fetch history and goal when active session changes
    useEffect(() => {
        if (activeSessionId) {
            fetchHistory(activeSessionId);
            fetchCurrentGoal(activeSessionId);
        } else {
            setCurrentGoal(null);
        }
    }, [activeSessionId]);

    const fetchCurrentGoal = async (sessionId) => {
        try {
            const response = await api.get('/goals/');
            const goal = response.data.find(g => g.session_id === sessionId);
            setCurrentGoal(goal || null);
        } catch (err) {
            console.error("Failed to fetch goal for session");
        }
    };

    const fetchHistory = async (sessionId) => {
        setLoading(true);
        try {
            const response = await api.get(`/chat/history/${sessionId}`);
            setMessages(response.data);
        } catch (err) {
            console.error("Failed to fetch history");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        let currentSessionId = activeSessionId;

        if (!currentSessionId) {
            try {
                const response = await api.post('/chat/sessions', { title: "New Chat" });
                const newSession = response.data;
                setSessions([newSession, ...sessions]);
                setActiveSessionId(newSession.id);
                currentSessionId = newSession.id;
            } catch (err) {
                console.error("Failed to create session");
                return;
            }
        }

        const userMsg = input;
        setInput('');
        setLoading(true);

        setStatus('Thinking...');

        // Optimistic update
        setMessages(prev => [...prev, { role: 'user', message: userMsg }]);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${api.defaults.baseURL}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ message: userMsg, session_id: currentSessionId })
            });

            if (!response.ok) throw new Error("Stream request failed");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedText = "";
            let agentMsgAdded = false;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);

                        if (data.type === 'status') {
                            setStatus(data.text);
                        } else if (data.type === 'chat_start') {
                            if (!agentMsgAdded) {
                                setMessages(prev => [...prev, { role: 'agent', message: "", type: 'chat' }]);
                                agentMsgAdded = true;
                            }
                        } else if (data.type === 'chat_chunk') {
                            accumulatedText += data.text;
                            setMessages(prev => {
                                const newMsgs = [...prev];
                                const last = newMsgs[newMsgs.length - 1];
                                if (last.role === 'agent') {
                                    last.message = accumulatedText;
                                }
                                return newMsgs;
                            });
                        } else if (data.type === 'plan' || data.type === 'resources') {
                            setMessages(prev => {
                                const newMsgs = [...prev];
                                const last = newMsgs[newMsgs.length - 1];
                                if (last.role === 'agent') {
                                    last.type = data.type;
                                    last.content = data.content;
                                }
                                return newMsgs;
                            });
                        } else if (data.type === 'error') {
                            setMessages(prev => [...prev, { role: 'agent', message: data.text, type: 'error' }]);
                        }
                    } catch (e) {
                        console.error("Error parsing stream chunk", e, line);
                    }
                }
            }

            // Refresh sessions and current goal after stream ends
            fetchSessions();
            if (currentSessionId) fetchCurrentGoal(currentSessionId);
        } catch (err) {
            console.error("Failed to send message", err);
            setMessages(prev => [...prev, { role: 'agent', message: "Sorry, I encountered an error connecting to the server.", type: 'error' }]);
        } finally {
            setLoading(false);
            setStatus('');
        }
    };

    const renderContent = (msg) => {
        if (msg.type === 'plan' && msg.content) {
            const plan = msg.content;
            return (
                <div className="mt-4 bg-indigo-50 p-4 rounded-xl border border-indigo-100 text-sm">
                    <h4 className="font-bold text-indigo-900 mb-2">Study Plan Overview</h4>
                    <p className="mb-4 text-indigo-700">{plan.overview}</p>
                    <div className="space-y-4">
                        {plan.weekly_schedule?.map((week) => (
                            <div key={week.week} className="bg-white p-3 rounded-lg shadow-sm">
                                <h5 className="font-semibold text-gray-800">Week {week.week}</h5>
                                <ul className="list-disc list-inside text-gray-600 mt-2">
                                    {week.activities.map((act, i) => <li key={i}>{act}</li>)}
                                </ul>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }
        if (msg.type === 'resources' && msg.content) {
            const { videos, web } = msg.content;
            return (
                <div className="mt-4 space-y-4">
                    {videos && videos.length > 0 && (
                        <div>
                            <h4 className="text-sm font-bold text-gray-700 mb-2 flex items-center">
                                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                                Recommended Videos
                            </h4>
                            <div className="grid gap-2">
                                {videos.map((res, i) => (
                                    <a key={i} href={res.url} target="_blank" rel="noopener noreferrer" className="block p-3 bg-white border border-gray-200 rounded-lg hover:border-indigo-300 transition-all hover:shadow-sm">
                                        <div className="font-semibold text-indigo-600 text-sm truncate">{res.title}</div>
                                        <div className="text-[10px] text-gray-500 uppercase tracking-wider">{res.channel}</div>
                                    </a>
                                ))}
                            </div>
                        </div>
                    )}
                    {web && web.length > 0 && (
                        <div>
                            <h4 className="text-sm font-bold text-gray-700 mb-2 flex items-center">
                                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                Documentation & Articles
                            </h4>
                            <div className="grid gap-2">
                                {web.map((res, i) => (
                                    <a key={i} href={res.url} target="_blank" rel="noopener noreferrer" className="block p-3 bg-white border border-gray-200 rounded-lg hover:border-blue-300 transition-all hover:shadow-sm">
                                        <div className="font-semibold text-blue-600 text-sm truncate">{res.title}</div>
                                        <div className="text-[10px] text-gray-500 uppercase tracking-wider">{res.site}</div>
                                    </a>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )
        }
        return null;
    }

    return (
        <div className="flex h-[calc(100vh-8rem)] bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
            {/* Sidebar */}
            <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-gray-50 border-r border-gray-200 transition-all duration-300 flex flex-col`}>
                <div className="p-4 border-b border-gray-200">
                    <button
                        onClick={createNewSession}
                        className="w-full bg-indigo-600 text-white px-4 py-2 rounded-xl hover:bg-indigo-700 transition flex items-center justify-center space-x-2 shadow-sm"
                    >
                        <Plus className="w-4 h-4" />
                        <span>New Chat</span>
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {sessions.map(session => (
                        <div key={session.id} className="group relative">
                            {editingSessionId === session.id ? (
                                <input
                                    autoFocus
                                    className="w-full text-left px-3 py-2 rounded-lg text-sm bg-white border border-indigo-300 outline-none"
                                    value={editTitle}
                                    onChange={(e) => setEditTitle(e.target.value)}
                                    onBlur={() => setEditingSessionId(null)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') handleRenameSession(session.id, e);
                                        if (e.key === 'Escape') setEditingSessionId(null);
                                    }}
                                />
                            ) : (
                                <button
                                    onClick={() => setActiveSessionId(session.id)}
                                    className={`w-full text-left px-3 py-2 pr-10 rounded-lg text-sm truncate transition-colors ${activeSessionId === session.id ? 'bg-indigo-100 text-indigo-700 font-medium' : 'text-gray-600 hover:bg-gray-100'}`}
                                >
                                    {session.title}
                                </button>
                            )}

                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setActiveMenuId(activeMenuId === session.id ? null : session.id);
                                }}
                                className={`absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 transition-opacity ${activeMenuId === session.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}
                            >
                                <MoreHorizontal className="w-4 h-4" />
                            </button>

                            {activeMenuId === session.id && (
                                <div className="absolute right-2 top-full mt-1 w-32 bg-white border border-gray-200 rounded-lg shadow-lg z-50 py-1">
                                    <button
                                        onClick={(e) => startEditing(session, e)}
                                        className="w-full text-left px-3 py-1.5 text-xs text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                                    >
                                        <Pencil className="w-3 h-3" />
                                        <span>Rename</span>
                                    </button>
                                    <button
                                        onClick={(e) => handleDeleteSession(session.id, e)}
                                        className="w-full text-left px-3 py-1.5 text-xs text-red-600 hover:bg-red-50 flex items-center space-x-2"
                                    >
                                        <Trash2 className="w-3 h-3" />
                                        <span>Delete</span>
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col min-w-0">
                <div className="bg-white border-b border-gray-100 p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 hover:bg-gray-100 rounded-lg text-gray-500">
                            <Menu className="w-5 h-5" />
                        </button>
                        <div className="font-semibold text-gray-800 flex items-center space-x-2">
                            <Bot className="w-5 h-5 text-indigo-600" />
                            <span>AI Learning Assistant</span>
                        </div>
                    </div>
                    {currentGoal && (
                        <div className="hidden md:flex items-center space-x-4 bg-indigo-50 px-4 py-2 rounded-2xl border border-indigo-100">
                            <div className="flex flex-col">
                                <span className="text-[10px] uppercase font-bold text-indigo-400">Target Mission</span>
                                <span className="text-xs font-bold text-indigo-900 truncate max-w-[200px]">{currentGoal.text}</span>
                            </div>
                            <div className="flex flex-col items-end">
                                <span className="text-[10px] uppercase font-bold text-indigo-400">Progress</span>
                                <span className="text-xs font-bold text-indigo-600">{currentGoal.progress}%</span>
                            </div>
                        </div>
                    )}
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                    {messages.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-gray-400">
                            <MessageSquare className="w-12 h-12 mb-2 opacity-20" />
                            <p>Start a new conversation</p>
                        </div>
                    )}
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none shadow-sm'}`}>
                                <p className="whitespace-pre-wrap leading-relaxed">{msg.message}</p>
                                {renderContent(msg)}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-white text-gray-800 border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-none shadow-sm flex items-center space-x-2">
                                <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                                <span className="text-sm text-gray-500">{status || 'Thinking...'}</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-100">
                    <div className="flex space-x-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your goal or question..."
                            className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all bg-gray-50 focus:bg-white text-gray-900 placeholder-gray-500"
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Chat;
