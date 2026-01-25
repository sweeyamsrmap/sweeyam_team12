import { Link } from 'react-router-dom';
import { ArrowRight, Brain, Target, Zap } from 'lucide-react';

const Home = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] text-center space-y-8 relative">
            <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-6xl drop-shadow-sm">
                Master Any Skill with <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">AI-Powered Planning</span>
            </h1>
            <p className="max-w-2xl text-xl text-slate-400">
                Stop wasting time figuring out *what* to study. Let our autonomous agent create personalized plans, find resources, and track your progress.
            </p>

            <div className="flex space-x-4">
                <Link to="/register" className="flex items-center space-x-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-full font-bold hover:from-indigo-500 hover:to-purple-500 transition-all shadow-lg hover:shadow-indigo-500/25 transform hover:-translate-y-1">
                    <span>Start Learning</span>
                    <ArrowRight className="w-5 h-5" />
                </Link>
                <Link to="/about" className="flex items-center space-x-2 bg-slate-800/50 text-white border border-slate-700 px-8 py-4 rounded-full font-bold hover:bg-slate-800 transition-all backdrop-blur-sm">
                    <span>Learn More</span>
                </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 text-left w-full">
                <div className="p-6 bg-slate-900/50 backdrop-blur-md rounded-xl shadow-xl border border-white/5 hover:border-indigo-500/30 transition-colors">
                    <div className="bg-indigo-500/10 w-fit p-3 rounded-lg mb-4">
                        <Target className="w-8 h-8 text-indigo-400" />
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-white">Smart Goal Setting</h3>
                    <p className="text-slate-400">Define your detailed learning goals and deadlines. We break them down.</p>
                </div>
                <div className="p-6 bg-slate-900/50 backdrop-blur-md rounded-xl shadow-xl border border-white/5 hover:border-purple-500/30 transition-colors">
                    <div className="bg-purple-500/10 w-fit p-3 rounded-lg mb-4">
                        <Brain className="w-8 h-8 text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-white">Adaptive Planning</h3>
                    <p className="text-slate-400">Get specific weekly schedules tailored to your pace and weak areas.</p>
                </div>
                <div className="p-6 bg-slate-900/50 backdrop-blur-md rounded-xl shadow-xl border border-white/5 hover:border-blue-500/30 transition-colors">
                    <div className="bg-blue-500/10 w-fit p-3 rounded-lg mb-4">
                        <Zap className="w-8 h-8 text-blue-400" />
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-white">Curated Resources</h3>
                    <p className="text-slate-400">Skip the search. Get the best videos, articles, and tests instantly.</p>
                </div>
            </div>
        </div>
    );
};

export default Home;
