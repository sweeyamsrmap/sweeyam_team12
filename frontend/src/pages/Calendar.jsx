import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Calendar as CalendarIcon, Clock, CheckCircle, Circle, ArrowLeft, ArrowRight, Zap } from 'lucide-react';

const Calendar = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [currentDate, setCurrentDate] = useState(new Date());

    useEffect(() => {
        fetchEvents();
    }, []);

    const fetchEvents = async () => {
        setLoading(true);
        try {
            const response = await api.get('/calendar/');
            setEvents(response.data);
        } catch (err) {
            console.error("Failed to fetch calendar events");
        } finally {
            setLoading(false);
        }
    };

    const toggleComplete = async (eventId) => {
        try {
            await api.patch(`/calendar/${eventId}/complete`);
            setEvents(prev => prev.map(e => e.id === eventId ? { ...e, is_completed: true } : e));
        } catch (err) {
            console.error("Failed to complete event");
        }
    };

    const formatTime = (isoString) => {
        return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const formatDate = (isoString) => {
        return new Date(isoString).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
    };

    // Simple grouping by date
    const groupedEvents = events.reduce((groups, event) => {
        const date = new Date(event.start_time).toLocaleDateString();
        if (!groups[date]) groups[date] = [];
        groups[date].push(event);
        return groups;
    }, {});

    return (
        <div className="max-w-5xl mx-auto space-y-10 py-6 animate-in fade-in duration-700">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight text-white">
                        Your <span className="text-gradient">Learning Schedule</span>
                    </h1>
                    <p className="text-slate-400 mt-2 font-medium">Autonomous planning synchronized with your goals.</p>
                </div>
                <div className="flex items-center space-x-4 bg-white/5 p-2 rounded-2xl border border-white/5">
                    <button className="p-2 hover:bg-white/5 rounded-xl text-slate-400">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <span className="text-sm font-bold text-white px-4">
                        {currentDate.toLocaleDateString([], { month: 'long', year: 'numeric' })}
                    </span>
                    <button className="p-2 hover:bg-white/5 rounded-xl text-slate-400">
                        <ArrowRight className="w-5 h-5" />
                    </button>
                </div>
            </header>

            {loading ? (
                <div className="grid gap-6">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-24 glass-card rounded-3xl animate-pulse"></div>
                    ))}
                </div>
            ) : Object.keys(groupedEvents).length === 0 ? (
                <div className="py-24 glass-card rounded-[3rem] text-center space-y-6">
                    <div className="bg-indigo-500/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto">
                        <CalendarIcon className="w-10 h-10 text-indigo-400" />
                    </div>
                    <div className="space-y-2">
                        <h3 className="text-2xl font-bold text-white">Empty Agenda</h3>
                        <p className="text-slate-400 max-w-xs mx-auto">
                            Ask your agent to schedule some study sessions for your active goals!
                        </p>
                    </div>
                </div>
            ) : (
                <div className="space-y-12">
                    {Object.entries(groupedEvents).map(([date, dayEvents]) => (
                        <div key={date} className="space-y-6">
                            <h3 className="text-lg font-bold text-slate-400 flex items-center space-x-3">
                                <span className="px-3 py-1 bg-white/5 rounded-lg border border-white/5">{date}</span>
                                <div className="h-px flex-1 bg-white/5"></div>
                            </h3>
                            <div className="grid gap-4">
                                {dayEvents.map(event => (
                                    <div key={event.id} className="group relative glass-card p-6 rounded-3xl hover:bg-slate-800/40 transition-all duration-300 border border-white/5">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-6">
                                                <div className="flex flex-col items-center justify-center min-w-[80px] py-1 border-r border-white/5 pr-6">
                                                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-tighter">Start</span>
                                                    <span className="text-lg font-black text-white">{formatTime(event.start_time)}</span>
                                                </div>
                                                <div>
                                                    <h4 className={`text-xl font-bold ${event.is_completed ? 'text-slate-500 line-through' : 'text-white'}`}>
                                                        {event.title}
                                                    </h4>
                                                    <div className="flex items-center space-x-4 mt-1">
                                                        <div className="flex items-center space-x-1 text-slate-500 text-xs font-medium">
                                                            <Clock className="w-3 h-3" />
                                                            <span>{Math.round((new Date(event.end_time) - new Date(event.start_time)) / 60000)} min session</span>
                                                        </div>
                                                        {event.is_completed && (
                                                            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full font-bold uppercase border border-emerald-500/20">
                                                                Done
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => !event.is_completed && toggleComplete(event.id)}
                                                className={`p-3 rounded-2xl transition-all ${event.is_completed ? 'bg-emerald-500/10 text-emerald-400' : 'bg-white/5 text-slate-600 hover:text-white hover:bg-white/10'}`}
                                            >
                                                {event.is_completed ? <CheckCircle className="w-6 h-6" /> : <Circle className="w-6 h-6" />}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className="glass-card p-8 rounded-[2.5rem] bg-indigo-600/10 border-indigo-500/20 flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center space-x-4 text-center md:text-left">
                    <div className="p-4 bg-indigo-500/20 rounded-2xl text-indigo-400">
                        <Zap className="w-8 h-8" />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white font-display">Need a custom plan?</h3>
                        <p className="text-slate-400 text-sm">Ask the agent to reschedule or find better slots for your speed.</p>
                    </div>
                </div>
                <Link to="/chat" className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl transition-all shadow-glow">
                    Talk to Agent
                </Link>
            </div>
        </div>
    );
};

export default Calendar;
