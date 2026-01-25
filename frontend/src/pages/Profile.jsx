import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { User, Mail, Edit2, Save, X, Target, MessageSquare, TrendingUp } from 'lucide-react';

const Profile = () => {
    const [profile, setProfile] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(false);
    const [formData, setFormData] = useState({
        username: '',
        bio: ''
    });

    useEffect(() => {
        fetchProfile();
        fetchStats();
    }, []);

    const fetchProfile = async () => {
        try {
            const response = await api.get('/profile/me');
            setProfile(response.data);
            setFormData({
                username: response.data.username || '',
                bio: response.data.bio || ''
            });
        } catch (err) {
            console.error("Failed to fetch profile");
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await api.get('/profile/stats');
            setStats(response.data);
        } catch (err) {
            console.error("Failed to fetch stats");
        }
    };

    const handleSave = async () => {
        try {
            const response = await api.patch('/profile/me', formData);
            setProfile(response.data);
            setEditing(false);
        } catch (err) {
            console.error("Failed to update profile", err);
            alert(err.response?.data?.detail || "Failed to update profile");
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto px-4 py-10 space-y-8 animate-in fade-in duration-700">
            {/* Header */}
            <header>
                <h1 className="text-4xl font-extrabold tracking-tight text-white">
                    Your <span className="text-gradient">Profile</span>
                </h1>
                <p className="text-slate-400 mt-2 font-medium">Manage your account and view your learning progress</p>
            </header>

            {/* Profile Card */}
            <div className="glass-card p-8 rounded-[3rem] space-y-6">
                <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-6">
                        <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">
                            {profile?.username ? profile.username[0].toUpperCase() : profile?.name[0].toUpperCase()}
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white">{profile?.name}</h2>
                            <p className="text-slate-400 flex items-center space-x-2 mt-1">
                                <Mail className="w-4 h-4" />
                                <span>{profile?.email}</span>
                            </p>
                        </div>
                    </div>

                    {!editing ? (
                        <button
                            onClick={() => setEditing(true)}
                            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all"
                        >
                            <Edit2 className="w-4 h-4" />
                            <span>Edit Profile</span>
                        </button>
                    ) : (
                        <div className="flex space-x-2">
                            <button
                                onClick={handleSave}
                                className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl transition-all"
                            >
                                <Save className="w-4 h-4" />
                                <span>Save</span>
                            </button>
                            <button
                                onClick={() => {
                                    setEditing(false);
                                    setFormData({
                                        username: profile?.username || '',
                                        bio: profile?.bio || ''
                                    });
                                }}
                                className="flex items-center space-x-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all"
                            >
                                <X className="w-4 h-4" />
                                <span>Cancel</span>
                            </button>
                        </div>
                    )}
                </div>

                <div className="space-y-4 pt-6 border-t border-white/10">
                    <div>
                        <label className="block text-sm font-bold text-slate-400 mb-2">Username</label>
                        {editing ? (
                            <input
                                type="text"
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                placeholder="Choose a username"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 outline-none"
                            />
                        ) : (
                            <p className="text-white text-lg">{profile?.username || <span className="text-slate-500 italic">Not set</span>}</p>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-bold text-slate-400 mb-2">Bio</label>
                        {editing ? (
                            <textarea
                                value={formData.bio}
                                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                                placeholder="Tell us about yourself..."
                                rows={4}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
                            />
                        ) : (
                            <p className="text-white">{profile?.bio || <span className="text-slate-500 italic">No bio yet</span>}</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                    { label: 'Total Goals', value: stats?.total_goals || 0, icon: Target, color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
                    { label: 'Active Goals', value: stats?.active_goals || 0, icon: TrendingUp, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
                    { label: 'Completed', value: stats?.completed_goals || 0, icon: Target, color: 'text-purple-400', bg: 'bg-purple-500/10' },
                    { label: 'Chat Sessions', value: stats?.total_sessions || 0, icon: MessageSquare, color: 'text-blue-400', bg: 'bg-blue-500/10' },
                ].map((stat, i) => (
                    <div key={i} className="glass-card p-6 rounded-2xl text-center space-y-3">
                        <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center mx-auto`}>
                            <stat.icon className={`w-6 h-6 ${stat.color}`} />
                        </div>
                        <div>
                            <p className="text-3xl font-bold text-white">{stat.value}</p>
                            <p className="text-sm text-slate-400 font-medium">{stat.label}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Average Progress */}
            {stats && stats.total_goals > 0 && (
                <div className="glass-card p-8 rounded-[2.5rem]">
                    <h3 className="text-xl font-bold text-white mb-4">Overall Progress</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-400">Average across all goals</span>
                            <span className="text-white font-bold">{stats.total_progress}%</span>
                        </div>
                        <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-1000"
                                style={{ width: `${stats.total_progress}%` }}
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* Quick Actions */}
            <div className="glass-card p-6 rounded-[2.5rem] flex flex-col md:flex-row items-center justify-between gap-4">
                <div>
                    <h3 className="text-xl font-bold text-white">Ready to learn more?</h3>
                    <p className="text-slate-400 text-sm">Set new goals and continue your journey</p>
                </div>
                <Link
                    to="/dashboard"
                    className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl transition-all"
                >
                    Go to Dashboard
                </Link>
            </div>
        </div>
    );
};

export default Profile;
