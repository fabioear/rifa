import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/logo.png';

interface TopbarProps {
    onToggleMenu: () => void;
}

const Topbar: React.FC<TopbarProps> = ({ onToggleMenu }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [imgError, setImgError] = useState(false);

    const getImageUrl = () => {
        if (!user?.avatar_url) return null;
        if (user.avatar_url.startsWith('http')) return user.avatar_url;
        
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const cleanApiUrl = apiUrl.replace(/\/api\/v1\/?$/, '');
        const prefix = cleanApiUrl.endsWith('/') ? cleanApiUrl.slice(0, -1) : cleanApiUrl;
        const path = user.avatar_url.startsWith('/') ? user.avatar_url : `/${user.avatar_url}`;
        
        // Add timestamp to prevent caching if needed, though simpler without for now unless update is frequent
        return `${prefix}${path}`;
    };

    const imageUrl = getImageUrl();

    return (
        <div className="h-[60px] bg-white dark:bg-slate-800 text-slate-900 dark:text-white flex justify-between items-center px-5 fixed top-0 left-0 right-0 z-[1000] border-b border-slate-200 dark:border-slate-700 transition-colors duration-200">
            <div className="flex items-center gap-3">
                <button 
                    onClick={onToggleMenu}
                    className="md:hidden p-2 -ml-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-md"
                    aria-label="Menu"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                    </svg>
                </button>

                <div 
                    className="font-bold text-xl cursor-pointer flex items-center gap-3" 
                    onClick={() => navigate('/')}
                >
                    <img src={logo} alt="Império das Rifas" className="h-10 w-auto" />
                    <span className="hidden sm:inline">Império das Rifas</span>
                </div>
            </div>
            
            <div className="flex items-center gap-5">
                {user && (
                    <>
                        <div className="text-sm">
                            <span className="text-slate-500 dark:text-slate-400 font-medium">{user.role === 'admin' ? 'ADMIN' : 'JOGADOR'}</span>
                        </div>
                        
                        <button 
                            onClick={() => navigate('/perfil')}
                            className="pl-2 pr-4 py-1.5 bg-transparent text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-600 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-2"
                        >
                            <div className="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex items-center justify-center border border-slate-300 dark:border-slate-600">
                                {imageUrl && !imgError ? (
                                    <img 
                                        src={imageUrl} 
                                        alt="Perfil" 
                                        className="h-full w-full object-cover"
                                        onError={() => setImgError(true)}
                                    />
                                ) : (
                                    <span className="text-lg">👤</span>
                                )}
                            </div>
                            <span>Perfil</span>
                        </button>

                        <button 
                            onClick={logout}
                            className="px-4 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 transition-colors border-none"
                        >
                            Sair
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};

export default Topbar;
