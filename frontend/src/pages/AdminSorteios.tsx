import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Sorteio } from '../types';
import { mapApiError } from '../utils/mapApiError';

const AdminSorteios: React.FC = () => {
    const { token } = useAuth();
    const [sorteios, setSorteios] = useState<Sorteio[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);

    const [formData, setFormData] = useState({
        nome: '',
        horario: '',
        ativo: true
    });

    useEffect(() => {
        fetchSorteios();
    }, []);

    const fetchSorteios = async () => {
        try {
            setLoading(true);
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            const response = await axios.get(`${apiUrl}/sorteios/?only_active=false`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setSorteios(response.data);
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
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            if (editingId) {
                await axios.put(`${apiUrl}/sorteios/${editingId}`, formData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            } else {
                await axios.post(`${apiUrl}/sorteios/`, formData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            }
            setShowForm(false);
            setEditingId(null);
            setFormData({ nome: '', horario: '', ativo: true });
            fetchSorteios();
        } catch (err) {
            console.error(err);
            alert(mapApiError(err));
        }
    };

    const handleEdit = (sorteio: Sorteio) => {
        setFormData({
            nome: sorteio.nome,
            horario: sorteio.horario ? sorteio.horario.substring(0, 5) : '', // Ensure HH:MM
            ativo: sorteio.ativo
        });
        setEditingId(sorteio.id);
        setShowForm(true);
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Tem certeza que deseja excluir este sorteio?')) return;
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            await axios.delete(`${apiUrl}/sorteios/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchSorteios();
        } catch (err) {
            console.error(err);
            alert(mapApiError(err));
        }
    };

    const handleNew = () => {
        setFormData({ nome: '', horario: '', ativo: true });
        setEditingId(null);
        setShowForm(true);
    };

    const handleCancel = () => {
        setShowForm(false);
        setEditingId(null);
    };

    return (
        <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Locais de Sorteio</h1>
                <button 
                    onClick={handleNew}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors"
                >
                    Novo Local
                </button>
            </div>

            {showForm && (
                <div className="mb-8 bg-white dark:bg-slate-800 p-6 rounded-lg shadow">
                    <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">
                        {editingId ? 'Editar Local' : 'Novo Local'}
                    </h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nome do Local</label>
                            <input 
                                type="text" 
                                value={formData.nome}
                                onChange={e => setFormData({...formData, nome: e.target.value})}
                                className="mt-1 block w-full rounded-md border-gray-300 dark:border-slate-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:text-white sm:text-sm px-3 py-2"
                                required
                            />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Horário do Sorteio</label>
                                <input 
                                    type="time" 
                                    value={formData.horario}
                                    onChange={e => setFormData({...formData, horario: e.target.value})}
                                    className="mt-1 block w-full rounded-md border-gray-300 dark:border-slate-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-slate-700 dark:text-white sm:text-sm px-3 py-2"
                                    required
                                />
                            </div>
                        </div>
                        <div className="flex items-center">
                            <input 
                                type="checkbox" 
                                checked={formData.ativo}
                                onChange={e => setFormData({...formData, ativo: e.target.checked})}
                                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                            <label className="ml-2 block text-sm text-gray-900 dark:text-white">Ativo</label>
                        </div>
                        <div className="flex justify-end space-x-3">
                            <button 
                                type="button" 
                                onClick={handleCancel}
                                className="bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-md hover:bg-gray-300 dark:hover:bg-slate-600"
                            >
                                Cancelar
                            </button>
                            <button 
                                type="submit" 
                                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                            >
                                Salvar
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="bg-white dark:bg-slate-800 shadow overflow-hidden sm:rounded-lg">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
                    <thead className="bg-gray-50 dark:bg-slate-700">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Nome</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Horário</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-slate-800 divide-y divide-gray-200 dark:divide-slate-700">
                        {sorteios.map((sorteio) => (
                            <tr key={sorteio.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{sorteio.nome}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{sorteio.horario}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${sorteio.ativo ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}`}>
                                        {sorteio.ativo ? 'Ativo' : 'Inativo'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button onClick={() => handleEdit(sorteio)} className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 mr-4">Editar</button>
                                    <button onClick={() => handleDelete(sorteio.id)} className="text-red-600 dark:text-red-400 hover:text-red-900">Excluir</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {loading && <div className="p-4 text-center text-gray-500 dark:text-gray-400">Carregando...</div>}
                {!loading && sorteios.length === 0 && <div className="p-4 text-center text-gray-500 dark:text-gray-400">Nenhum sorteio encontrado.</div>}
            </div>
        </div>
    );
};

export default AdminSorteios;