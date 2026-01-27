import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../hooks/useTheme';
import PasswordStrength from '../components/PasswordStrength';
import { mapApiError } from '../utils/mapApiError';
import { errorsPT } from '../i18n/errors.pt-BR';

const Profile: React.FC = () => {
    const { user, logout } = useAuth();
    const { mode, toggleTheme } = useTheme();

    // Mock initial state since backend doesn't provide all these fields yet
    const [name, setName] = useState('Usuário');
    const [email, setEmail] = useState(user?.email || '');
    const [whatsappEnabled, setWhatsappEnabled] = useState(true);
    
    // Password Change State
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [isPasswordValid, setIsPasswordValid] = useState(false);
    
    // UI State
    const [isEditing, setIsEditing] = useState(false);
    const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'preferences'>('profile');
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    useEffect(() => {
        if (user?.email) setEmail(user.email);
    }, [user]);

    const handleSaveProfile = (e: React.FormEvent) => {
        e.preventDefault();
        // Mock API call
        setMessage({ type: 'success', text: 'Perfil atualizado com sucesso!' });
        setIsEditing(false);
        setTimeout(() => setMessage(null), 3000);
    };

    const handleChangePassword = (e: React.FormEvent) => {
        e.preventDefault();
        if (newPassword !== confirmNewPassword) {
            setMessage({ type: 'error', text: errorsPT.passwordsDontMatch });
            return;
        }
        if (!isPasswordValid) {
            setMessage({ type: 'error', text: errorsPT.passwordRules });
            return;
        }
        
        // Mock API call
        setMessage({ type: 'success', text: 'Senha alterada com sucesso!' });
        setCurrentPassword('');
        setNewPassword('');
        setConfirmNewPassword('');
        setTimeout(() => setMessage(null), 3000);
    };

    const handleThemeToggle = () => {
        toggleTheme();
        // Sync with backend
        // axios.patch('/api/v1/users/me/preferences', { theme: mode === 'dark' ? 'light' : 'dark' }).catch(console.error);
    };

    return (
        <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
            <div className="md:flex md:items-center md:justify-between mb-8">
                <div className="flex-1 min-w-0">
                    <h2 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
                        Configurações da Conta
                    </h2>
                </div>
            </div>

            {message && (
                <div className={`mb-4 p-4 rounded-md ${message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30' : 'bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30'}`}>
                    {message.text}
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
                <div className="border-b border-gray-200 dark:border-gray-700">
                    <nav className="-mb-px flex" aria-label="Tabs">
                        <button
                            onClick={() => setActiveTab('profile')}
                            className={`${activeTab === 'profile' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'} w-1/3 py-4 px-1 text-center border-b-2 font-medium text-sm transition-colors duration-200`}
                        >
                            Perfil
                        </button>
                        <button
                            onClick={() => setActiveTab('security')}
                            className={`${activeTab === 'security' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'} w-1/3 py-4 px-1 text-center border-b-2 font-medium text-sm transition-colors duration-200`}
                        >
                            Segurança
                        </button>
                        <button
                            onClick={() => setActiveTab('preferences')}
                            className={`${activeTab === 'preferences' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'} w-1/3 py-4 px-1 text-center border-b-2 font-medium text-sm transition-colors duration-200`}
                        >
                            Preferências
                        </button>
                    </nav>
                </div>

                <div className="p-6">
                    {activeTab === 'profile' && (
                        <form onSubmit={handleSaveProfile}>
                            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                                <div className="sm:col-span-3">
                                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                        Nome
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="text"
                                            name="name"
                                            id="name"
                                            disabled={!isEditing}
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 dark:text-white disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:text-gray-500"
                                        />
                                    </div>
                                </div>

                                <div className="sm:col-span-4">
                                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                        Endereço de e-mail
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            id="email"
                                            name="email"
                                            type="email"
                                            disabled={!isEditing}
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 dark:text-white disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:text-gray-500"
                                        />
                                    </div>
                                </div>
                            </div>
                            
                            <div className="mt-6 flex justify-end">
                                {!isEditing ? (
                                    <button
                                        type="button"
                                        onClick={() => setIsEditing(true)}
                                        className="bg-white dark:bg-gray-700 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        Editar
                                    </button>
                                ) : (
                                    <div className="flex space-x-3">
                                        <button
                                            type="button"
                                            onClick={() => setIsEditing(false)}
                                            className="bg-white dark:bg-gray-700 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600"
                                        >
                                            Cancelar
                                        </button>
                                        <button
                                            type="submit"
                                            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                        >
                                            Salvar
                                        </button>
                                    </div>
                                )}
                            </div>
                        </form>
                    )}

                    {activeTab === 'security' && (
                        <form onSubmit={handleChangePassword} className="space-y-6 max-w-lg">
                            <div>
                                <label htmlFor="current-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Senha atual
                                </label>
                                <input
                                    type="password"
                                    id="current-password"
                                    required
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:text-white"
                                />
                            </div>
                            
                            <div>
                                <label htmlFor="new-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Nova senha
                                </label>
                                <input
                                    type="password"
                                    id="new-password"
                                    required
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:text-white"
                                />
                                <PasswordStrength password={newPassword} onValidationChange={setIsPasswordValid} />
                            </div>

                            <div>
                                <label htmlFor="confirm-new-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Confirmar nova senha
                                </label>
                                <input
                                    type="password"
                                    id="confirm-new-password"
                                    required
                                    value={confirmNewPassword}
                                    onChange={(e) => setConfirmNewPassword(e.target.value)}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:text-white"
                                />
                            </div>

                            <div className="flex justify-end">
                                <button
                                    type="submit"
                                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                >
                                    Alterar Senha
                                </button>
                            </div>
                        </form>
                    )}

                    {activeTab === 'preferences' && (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-lg leading-6 font-medium text-slate-900 dark:text-slate-100">Aparência</h3>
                                    <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                                        Escolha entre modo claro e escuro.
                                    </p>
                                </div>
                                <button
                                    onClick={handleThemeToggle}
                                    type="button"
                                    className={`${mode === 'dark' ? 'bg-indigo-600' : 'bg-slate-200'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
                                >
                                    <span className="sr-only">Toggle Theme</span>
                                    <span
                                        aria-hidden="true"
                                        className={`${mode === 'dark' ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200 flex items-center justify-center`}
                                    >
                                        {mode === 'dark' ? '🌙' : '☀️'}
                                    </span>
                                </button>
                            </div>

                            <div className="border-t border-slate-200 dark:border-slate-700 pt-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="text-lg leading-6 font-medium text-slate-900 dark:text-slate-100">Notificações</h3>
                                        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                                            Receber atualizações e novidades via WhatsApp.
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => setWhatsappEnabled(!whatsappEnabled)}
                                        type="button"
                                        className={`${whatsappEnabled ? 'bg-green-600' : 'bg-slate-200'} relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500`}
                                    >
                                        <span className="sr-only">Toggle WhatsApp</span>
                                        <span
                                            aria-hidden="true"
                                            className={`${whatsappEnabled ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                                        />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Profile;
