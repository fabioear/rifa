import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import mascoteLogo from '../../assets/mascotelogo.png';

const Topbar: React.FC = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="h-[60px] bg-white dark:bg-slate-800 text-slate-900 dark:text-white flex justify-between items-center px-5 fixed top-0 left-0 right-0 z-[1000] border-b border-slate-200 dark:border-slate-700 transition-colors duration-200">
            <div 
                className="font-bold text-xl cursor-pointer flex items-center gap-3" 
                onClick={() => navigate('/')}
            >
                <img src={mascoteLogo} alt="Império das Rifas" className="h-10 w-auto" />
                Império das Rifas
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
