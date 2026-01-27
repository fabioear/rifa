import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar: React.FC = () => {
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
        <nav className="fixed left-0 top-[60px] h-[calc(100vh-60px)] w-[200px] bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 p-5 box-border overflow-y-auto transition-colors duration-200">
            <div className="mb-5 font-bold text-slate-900 dark:text-white uppercase text-xs tracking-wider">Menu</div>
            
            {/* Common Links */}
            <NavLink to="/rifas" className={getLinkClass}>Rifas</NavLink>

            {/* Admin Links */}
            {user.role === 'admin' && (
                <>
                    <NavLink to="/dashboard" className={getLinkClass}>Dashboard</NavLink>
                    <NavLink to="/admin-sorteios" className={getLinkClass}>Sorteios</NavLink>
                    <NavLink to="/admin-apuracao" className={getLinkClass}>Apuração</NavLink>
                    <NavLink to="/admin-settings" className={getLinkClass}>Configurações</NavLink>
                    <NavLink to="/usuarios" className={getLinkClass}>Usuários</NavLink>
                </>
            )}

            {/* Player Links */}
            {user.role === 'player' && (
                <NavLink to="/minhas-compras" className={getLinkClass}>Minhas Compras</NavLink>
            )}
        </nav>
    );
};

export default Navbar;
