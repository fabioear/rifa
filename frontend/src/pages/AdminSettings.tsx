import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { mapApiError } from '../utils/mapApiError';

const AdminSettings: React.FC = () => {
    const { token } = useAuth();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [fechamentoMinutos, setFechamentoMinutos] = useState<number>(20);

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            setLoading(true);
            const response = await axios.get('http://localhost:8000/api/v1/admin/settings', {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.data) {
                setFechamentoMinutos(response.data.fechamento_minutos);
            }
        } catch (err) {
            console.error(err);
            alert(mapApiError(err));
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setSaving(true);
            await axios.put('http://localhost:8000/api/v1/admin/settings', {
                fechamento_minutos: fechamentoMinutos
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            alert('Configurações salvas com sucesso!');
        } catch (err) {
            console.error(err);
            alert(mapApiError(err));
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <div className="p-5 text-gray-500 dark:text-gray-400">Carregando configurações...</div>;
    }

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Configurações do Sistema</h1>
            
            <div className="bg-white dark:bg-slate-800 shadow rounded-lg p-6">
                <form onSubmit={handleSubmit}>
                    <div className="mb-6">
                        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Regras de Fechamento</h2>
                        <div className="grid grid-cols-1 gap-6">
                            <div>
                                <label htmlFor="fechamentoMinutos" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Tempo de fechamento antes do sorteio (minutos)
                                </label>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                                    Quantos minutos antes do horário do sorteio as apostas devem ser encerradas.
                                </p>
                                <input
                                    type="number"
                                    id="fechamentoMinutos"
                                    min="0"
                                    value={fechamentoMinutos}
                                    onChange={(e) => setFechamentoMinutos(parseInt(e.target.value) || 0)}
                                    className="block w-full rounded-md border-gray-300 dark:border-slate-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:text-white sm:text-sm p-2 border"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end pt-4 border-t border-gray-200 dark:border-slate-700">
                        <button
                            type="submit"
                            disabled={saving}
                            className={`inline-flex justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                                saving ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
                            }`}
                        >
                            {saving ? 'Salvando...' : 'Salvar Configurações'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AdminSettings;
