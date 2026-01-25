import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from '../components/ToastProvider';
import api from '../services/api';
import { PlusCircle, Target, Clock, Zap, ArrowRight, BookOpen, Star, RefreshCw, CheckCircle } from 'lucide-react';

const Dashboard = () => {
    const [goals, setGoals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [goalInput, setGoalInput] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [isPlanning, setIsPlanning] = useState(false);
    const [todayEvents, setTodayEvents] = useState([]);
    const { addToast } = useToast();

    useEffect(() => {
        fetchGoals();
        fetchTodayAgenda();
        const pollNotifications = setInterval(async () => {
            try {
                const response = await api.get('/notifications/');
                const unread = response.data.filter(n => !n.is_read);
                if (unread.length > 0) {
                    const latest = unread[0];
                    addToast(latest.title, latest.message, latest.type === 'daily_task' ? 'alert' : 'info');
                    // Mark as read immediately to avoid double toasts in polling
                    await api.patch(`/notifications/${latest.id}/read`);
                }
            } catch (err) { }
        }, 30000); // Poll for autonomous interjections every 30s
        return () => clearInterval(pollNotifications);
    }, []);

    const fetchTodayAgenda = async () => {
        try {
            const response = await api.get('/calendar/');
            // Filter for today
            const today = new Date().toLocaleDateString();
            const filtered = response.data.filter(e => new Date(e.start_time).toLocaleDateString() === today);
            setTodayEvents(filtered);
        } catch (err) {
            console.error("Failed to fetch agenda");
        }
    };

    const fetchGoals = async () => {
        setLoading(true);
        try {
            const response = await api.get('/goals/');
            setGoals(response.data);
        } catch (err) {
            console.error("Failed to fetch goals");
        } finally {
            setLoading(false);
        }
    };

    const handleSetGoal = async (e) => {
        e.preventDefault();
        if (!goalInput.trim() || isCreating) return;

        setIsCreating(true);
        setIsPlanning(true);
        try {
            // 1. Create a new session
            const sessionResponse = await api.post('/chat/sessions', { title: goalInput.substring(0, 30) });
            const sessionId = sessionResponse.data.id;

            // 2. Send the goal as the first message to trigger plan generation
            const token = localStorage.getItem('token');
            // We don't await the full stream here, just the start
            fetch(`${api.defaults.baseURL}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ message: goalInput, session_id: sessionId })
            });

            // 3. Close modal and start polling
            setGoalInput('');
            setIsModalOpen(false);

            // Poll for the new goal - increased time for agent to process
            let attempts = 0;
            const poll = setInterval(async () => {
                attempts++;
                const response = await api.get('/goals/');
                if (response.data.length > goals.length || attempts > 20) {
                    setGoals(response.data);
                    setIsPlanning(false);
                    clearInterval(poll);
                }
            }, 3000); // Poll every 3 seconds for up to 60 seconds

        } catch (err) {
            console.error("Failed to set goal", err);
            setIsPlanning(false);
        } finally {
            setIsCreating(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12 animate-in fade-in duration-700">
            {/* Header Section */}
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="space-y-2">
                    <h1 className="text-5xl font-extrabold tracking-tight">
                        <span className="text-white text-high-contrast">Your </span>
                        <span className="text-gradient">Learning Dashboard</span>
                    </h1>
                    <p className="text-slate-400 text-lg max-w-2xl font-medium">
                        Accelerate your growth with AI-driven study plans and real-time goal tracking.
                    </p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="group flex items-center space-x-3 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-2xl transition-all duration-300 shadow-lg glow-btn"
                >
                    <Zap className="w-5 h-5 fill-current" />
                    <span className="font-bold text-lg">Set New Goal</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
            </header>

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-300">
                    <div className="bg-slate-900 border border-white/10 p-8 rounded-[2.5rem] w-full max-w-xl shadow-2xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 blur-[100px]"></div>

                        <div className="relative z-10 space-y-6">
                            <div className="flex items-center space-x-4">
                                <div className="p-3 bg-indigo-500/20 rounded-2xl text-indigo-400">
                                    <Target className="w-8 h-8" />
                                </div>
                                <div>
                                    <h2 className="text-2xl font-bold text-white">Define Your Mission</h2>
                                    <p className="text-slate-400">What would you like to achieve today?</p>
                                </div>
                            </div>

                            <form onSubmit={handleSetGoal} className="space-y-6">
                                <textarea
                                    autoFocus
                                    value={goalInput}
                                    onChange={(e) => setGoalInput(e.target.value)}
                                    placeholder="e.g., I want to learn React in 4 weeks and build a portfolio..."
                                    className="w-full h-32 bg-white/5 border border-white/10 rounded-2xl p-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 outline-none transition-all resize-none"
                                />
                                <div className="flex space-x-4">
                                    <button
                                        type="button"
                                        onClick={() => setIsModalOpen(false)}
                                        className="flex-1 py-4 bg-white/5 hover:bg-white/10 text-white font-bold rounded-2xl transition-all"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={isCreating || !goalInput.trim()}
                                        className="flex-1 py-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold rounded-2xl transition-all shadow-lg glow-btn flex items-center justify-center space-x-2"
                                    >
                                        {isCreating ? (
                                            <>
                                                <RefreshCw className="w-5 h-5 animate-spin" />
                                                <span>Planning...</span>
                                            </>
                                        ) : (
                                            <>
                                                <span>Launch Mission</span>
                                                <ArrowRight className="w-5 h-5" />
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}

            {/* Quick Stats / Feedback */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { label: 'Active Goals', value: goals.filter(g => g.status === 'active').length, icon: Target, color: 'text-indigo-400' },
                    { label: 'Upcoming Sessions', value: todayEvents.filter(e => !e.is_completed).length, icon: Clock, color: 'text-emerald-400' },
                    { label: 'Current Progress', value: goals.length > 0 ? `${Math.round(goals.reduce((acc, g) => acc + g.progress, 0) / goals.length)}%` : '0%', icon: Star, color: 'text-yellow-400' },
                ].map((stat, i) => (
                    <div key={i} className="glass-card p-6 rounded-3xl flex items-center space-x-5">
                        <div className={`p-4 rounded-2xl bg-white/5 ${stat.color}`}>
                            <stat.icon className="w-8 h-8" />
                        </div>
                        <div>
                            <p className="text-slate-400 font-medium text-sm uppercase tracking-wider">{stat.label}</p>
                            <p className="text-3xl font-bold text-white">{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Today's Agenda Widget */}
            <section className="animate-in slide-in-from-bottom-4 duration-1000 delay-200">
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-bold flex items-center space-x-3 text-white">
                        <Zap className="w-8 h-8 text-indigo-400 fill-indigo-400/20" />
                        <span>Today's Agenda</span>
                    </h2>
                    <Link to="/calendar" className="text-sm font-bold text-indigo-400 hover:text-indigo-300 transition-colors uppercase tracking-widest">
                        Full Schedule →
                    </Link>
                </div>

                <div className="glass-card p-8 rounded-[3rem] border-white/5 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 overflow-hidden relative">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 blur-[120px] -z-10"></div>

                    {todayEvents.length === 0 ? (
                        <div className="text-center py-6">
                            <p className="text-slate-500 font-medium">No sessions booked for today. Enjoy your break or start a new mission!</p>
                        </div>
                    ) : (
                        <div className="flex flex-col md:flex-row gap-6">
                            {todayEvents.slice(0, 3).map((event, i) => (
                                <div key={i} className="flex-1 bg-white/5 border border-white/5 p-6 rounded-[2rem] hover:bg-white/10 transition-all group">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="text-[10px] font-black text-indigo-400 uppercase tracking-widest px-3 py-1 bg-indigo-500/10 rounded-full">
                                            {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </div>
                                        {event.is_completed && <CheckCircle className="w-5 h-5 text-emerald-400" />}
                                    </div>
                                    <h4 className="text-lg font-bold text-white mb-2 group-hover:text-indigo-300 transition-colors line-clamp-1">{event.title}</h4>
                                    <div className="flex items-center space-x-2 text-slate-500 text-xs font-bold uppercase">
                                        <Clock className="w-3 h-3" />
                                        <span>30-45 MIN</span>
                                    </div>
                                </div>
                            ))}
                            {todayEvents.length > 3 && (
                                <Link to="/calendar" className="flex items-center justify-center px-8 border border-dashed border-white/10 rounded-[2rem] text-slate-500 hover:text-white hover:border-white/20 transition-all font-bold">
                                    +{todayEvents.length - 3} More
                                </Link>
                            )}
                        </div>
                    )}
                </div>
            </section>

            {/* Main Content */}
            <section>
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-bold flex items-center space-x-3">
                        <span className="w-2.5 h-10 bg-indigo-500 rounded-full shadow-[0_0_15px_rgba(99,102,241,0.5)]"></span>
                        <span className="text-white">Ongoing Missions</span>
                    </h2>
                    <button onClick={fetchGoals} className="p-3 glass-button rounded-xl text-slate-400 hover:text-white transition-colors">
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-64 glass-card rounded-3xl animate-pulse"></div>
                        ))}
                    </div>
                ) : (goals.length === 0 && !isPlanning) ? (
                    <div className="flex flex-col items-center justify-center py-24 glass-card rounded-[3rem] border-dashed border-white/5 space-y-8">
                        <div className="relative">
                            <div className="absolute inset-0 bg-indigo-500/20 blur-[100px] rounded-full"></div>
                            <img
                                src="/assets/empty_goals.png"
                                alt="No goals"
                                className="w-64 h-64 object-contain relative z-10 drop-shadow-2xl"
                            />
                        </div>
                        <div className="text-center space-y-4 max-w-md mx-auto px-6">
                            <h3 className="text-3xl font-bold text-white">Your journey starts here</h3>
                            <p className="text-slate-400 text-lg font-medium leading-relaxed">
                                You haven't defined any learning goals yet. Ask the agent to build your first autonomous study path.
                            </p>
                            <button
                                onClick={() => setIsModalOpen(true)}
                                className="inline-flex items-center space-x-2 text-indigo-400 hover:text-indigo-300 font-bold text-lg group pt-4"
                            >
                                <span>Set Your First Goal</span>
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-2 transition-transform" />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {isPlanning && (
                            <div className="group relative glass-card p-8 rounded-[2.5rem] bg-indigo-500/5 border-dashed border-indigo-500/30 animate-pulse flex flex-col justify-center items-center space-y-4">
                                <div className="p-4 rounded-2xl bg-indigo-500/20 text-indigo-400">
                                    <RefreshCw className="w-8 h-8 animate-spin" />
                                </div>
                                <div className="text-center">
                                    <h3 className="text-xl font-bold text-white">Planning Mission...</h3>
                                    <p className="text-slate-400 text-sm">Agent is drafting your roadmap</p>
                                </div>
                            </div>
                        )}
                        {goals.map((goal) => (
                            <div key={goal.id} className="group relative glass-card p-8 rounded-[2.5rem] hover:bg-slate-800/60 transition-all duration-500 overflow-hidden">
                                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 blur-[50px] group-hover:bg-indigo-500/20 transition-all"></div>

                                <div className="flex justify-between items-start mb-8 relative z-10">
                                    <div className="p-4 rounded-2xl bg-indigo-500/10 text-indigo-400 group-hover:scale-110 transition-transform duration-300">
                                        <Target className="w-8 h-8" />
                                    </div>
                                    <div className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest ${goal.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-700 text-slate-400'}`}>
                                        {goal.status}
                                    </div>
                                </div>

                                <div className="space-y-6 relative z-10">
                                    <h3 className="text-2xl font-bold leading-tight group-hover:text-indigo-400 transition-colors h-16 line-clamp-2">
                                        {goal.text}
                                    </h3>

                                    {/* Progress Section */}
                                    <div className="space-y-3">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-400 font-medium text-xs">Progress</span>
                                            <span className="text-white font-bold">{goal.progress}%</span>
                                        </div>
                                        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-1000"
                                                style={{ width: `${goal.progress}%` }}
                                            />
                                        </div>
                                        <div className="flex items-center space-x-2 text-[10px] text-slate-500 font-bold uppercase">
                                            <Zap className="w-3 h-3 text-indigo-400" />
                                            <span>{goal.completed_tasks} / {goal.total_tasks} milestones</span>
                                        </div>
                                    </div>

                                    <div className="flex items-center space-x-3 text-slate-400">
                                        <Clock className="w-4 h-4 text-indigo-400/60" />
                                        <span className="text-xs font-medium">Ends: {goal.deadline || '2 weeks'}</span>
                                    </div>
                                </div>

                                <div className="mt-8 pt-6 border-t border-white/5 flex items-center justify-between relative z-10">
                                    <div className="flex -space-x-2">
                                        {[1, 2, 3].map(i => (
                                            <div key={i} className="w-8 h-8 rounded-full border-2 border-slate-800 bg-slate-700 flex items-center justify-center text-[10px] font-bold">AI</div>
                                        ))}
                                    </div>
                                    <Link
                                        to={`/chat?sessionId=${goal.session_id}`}
                                        className="p-2 rounded-xl glass-button text-slate-400 hover:text-white transition-all focus:ring-2 focus:ring-indigo-500 outline-none"
                                    >
                                        <ArrowRight className="w-5 h-5" />
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>
        </div>
    );
};

export default Dashboard;
