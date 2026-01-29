import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

interface NavbarProps {
    isOpen: boolean;
    onClose: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ isOpen, onClose }) => {
    const { user } = useAuth();

    if (!user) return null;

    const getLinkClass = ({ isActive }: { isActive: boolean }) => `
        block px-4 py-2 mb-1 rounded-md transition-colors duration-200
        ${isActive 
            ? 'bg-indigo-600 text-white' 
            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-slate-100'
        }
    `;

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-20 md:hidden"
                    onClick={onClose}
                />
            )}
            
            <nav className={`fixed left-0 top-[60px] h-[calc(100vh-60px)] w-[200px] bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 p-5 box-border overflow-y-auto transition-transform duration-300 ease-in-out z-30 ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}>
                <div className="mb-5 font-bold text-slate-900 dark:text-white uppercase text-xs tracking-wider flex justify-between items-center">
                    <span>Menu</span>
                    <button onClick={onClose} className="md:hidden text-slate-500 hover:text-slate-700 dark:hover:text-slate-300">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                
                <div onClick={onClose}>
                    {/* Common Links */}
                    <NavLink to="/rifas" className={getLinkClass}>Rifas</NavLink>

                    {/* Admin Links */}
                    {user.role === 'admin' && (
                        <>
                            <NavLink to="/dashboard" className={getLinkClass}>Dashboard</NavLink>
                            <NavLink to="/admin-sorteios" className={getLinkClass}>Locais de Sorteio</NavLink>
                            <NavLink to="/admin-apuracao" className={getLinkClass}>Apuração</NavLink>
                            <NavLink to="/admin-settings" className={getLinkClass}>Configurações</NavLink>
                            <NavLink to="/usuarios" className={getLinkClass}>Usuários</NavLink>
                        </>
                    )}

                    {/* Player Links */}
                    {user.role === 'player' && (
                        <NavLink to="/minhas-compras" className={getLinkClass}>Minhas Compras</NavLink>
                    )}
                </div>
            </nav>
        </>
    );
};

export default Navbar;
