import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Rifa, RifaStatus } from '../types';
import { mapApiError } from '../utils/mapApiError';

const Rifas: React.FC = () => {
    const { token } = useAuth();
    const navigate = useNavigate();
    const [rifas, setRifas] = useState<Rifa[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filterStatus, setFilterStatus] = useState<string>('todas');

    useEffect(() => {
        fetchRifas();
    }, []);

    const fetchRifas = async () => {
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            const response = await axios.get(`${apiUrl}/rifas/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setRifas(response.data);
        } catch (err) {
            setError(mapApiError(err));
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const filteredRifas = rifas.filter(rifa => {
        if (filterStatus === 'todas') {
            // Default view: Only Active and Apuradas
            return rifa.status === RifaStatus.ATIVA || rifa.status === RifaStatus.APURADA;
        }
        return rifa.status === filterStatus;
    }).sort((a, b) => {
        // Sort logic: Active first, then Apuradas
        if (filterStatus === 'todas') {
            if (a.status === RifaStatus.ATIVA && b.status !== RifaStatus.ATIVA) return -1;
            if (a.status !== RifaStatus.ATIVA && b.status === RifaStatus.ATIVA) return 1;
        }
        return 0;
    });

    const getBorderColor = (status: RifaStatus) => {
        if (status === RifaStatus.ATIVA) return 'border-green-500 dark:border-green-600';
        if (status === RifaStatus.ENCERRADA) return 'border-red-500 dark:border-red-600';
        if (status === RifaStatus.APURADA) return 'border-red-500 dark:border-red-600';
        if (status === RifaStatus.RASCUNHO) return 'border-blue-500 dark:border-blue-600';
        return 'border-gray-200 dark:border-gray-700';
    };

    const getHeaderColor = (status: RifaStatus) => {
        if (status === RifaStatus.ATIVA) return 'bg-green-50 dark:bg-green-900/20 border-green-100 dark:border-green-900/30';
        if (status === RifaStatus.ENCERRADA) return 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-900/30';
        if (status === RifaStatus.APURADA) return 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-900/30';
        if (status === RifaStatus.RASCUNHO) return 'bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-900/30';
        return 'bg-gray-50 dark:bg-gray-700 border-gray-100 dark:border-gray-600';
    };

    const getTextColor = (status: RifaStatus) => {
        if (status === RifaStatus.ATIVA) return 'text-green-600 dark:text-green-400';
        if (status === RifaStatus.ENCERRADA) return 'text-red-600 dark:text-red-400';
        if (status === RifaStatus.APURADA) return 'text-red-600 dark:text-red-400';
        if (status === RifaStatus.RASCUNHO) return 'text-blue-600 dark:text-blue-400';
        return 'text-gray-600 dark:text-gray-400';
    };

    if (loading) return <div className="p-5 text-gray-900 dark:text-gray-100">Carregando rifas...</div>;
    if (error) return <div className="p-5 text-red-600 dark:text-red-400">{error}</div>;

    return (
        <div className="p-5 max-w-7xl mx-auto">
            <div className="flex flex-col sm:flex-row justify-between items-center mb-5 gap-4">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Rifas Disponíveis</h1>
                
                <div className="flex items-center gap-2">
                    <label htmlFor="statusFilter" className="text-sm font-medium text-gray-700 dark:text-gray-300">Filtrar por:</label>
                    <select
                        id="statusFilter"
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                    >
                        <option value="todas">Principais (Abertas/Apuradas)</option>
                        <option value={RifaStatus.ATIVA}>Em Aberto</option>
                        <option value={RifaStatus.ENCERRADA}>Encerradas</option>
                        <option value={RifaStatus.APURADA}>Apuradas</option>
                        <option value={RifaStatus.RASCUNHO}>Rascunho</option>
                    </select>
                </div>
            </div>

            {filteredRifas.length === 0 ? (
                <div className="p-10 text-center text-gray-500 bg-white dark:bg-gray-800 rounded-lg shadow">
                    <p>Nenhuma rifa encontrada com o filtro selecionado.</p>
                </div>
            ) : (
                <div className="grid grid-cols-[repeat(auto-fill,minmax(300px,1fr))] gap-5">
                    {filteredRifas.map((rifa) => (
                        <div key={rifa.id} className={`
                            bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border-2
                            ${getBorderColor(rifa.status)}
                        `}>
                            <div className={`
                                px-4 py-3 border-b
                                ${getHeaderColor(rifa.status)}
                            `}>
                                <div className="flex justify-between">
                                    <span className={`
                                        font-bold uppercase text-xs
                                        ${getTextColor(rifa.status)}
                                    `}>
                                        {rifa.status}
                                    </span>
                                    <span className="text-xs text-gray-500 dark:text-gray-400">
                                        {new Date(rifa.data_sorteio).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                            <div className="p-5">
                                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">{rifa.titulo}</h3>
                                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 min-h-[40px]">
                                    {rifa.descricao}
                                </p>
                                
                                <div className="flex gap-2.5 mb-4 text-xs text-gray-500 dark:text-gray-400">
                                    <span className="bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded">{rifa.tipo_rifa}</span>
                                    <span className="bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded">{rifa.local_sorteio}</span>
                                </div>

                                <div className="flex justify-between items-center">
                                    <div>
                                        <div className="text-xs text-gray-500 dark:text-gray-400">Preço</div>
                                        <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                                            R$ {Number(rifa.preco_numero).toFixed(2)}
                                        </div>
                                    </div>
                                    <button 
                                        onClick={() => navigate(`/rifas/${rifa.id}`)}
                                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                    >
                                        Ver Números
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Rifas;