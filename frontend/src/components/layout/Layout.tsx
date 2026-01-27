import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Navbar from './Navbar';
import Topbar from './Topbar';

const Layout: React.FC = () => {
    const { isAuthenticated, user } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // Prevent rendering layout without user data (avoids missing Navbar)
    if (!user) {
        return <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-white">Carregando...</div>;
    }

    return (
        <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-slate-900 transition-colors duration-200">
            <Topbar />
            <div className="flex flex-1 pt-[60px]">
                <Navbar />
                <main className="flex-1 ml-[200px] p-5 bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors duration-200">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;
