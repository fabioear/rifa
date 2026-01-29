import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/logo.png';

interface TopbarProps {
    onToggleMenu: () => void;
}

const Topbar: React.FC<TopbarProps> = ({ onToggleMenu }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

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
                            className="px-4 py-1.5 bg-transparent text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-600 rounded hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-2"
                        >
                            <span>👤</span> Perfil
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
