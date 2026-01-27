import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Rifa, RifaStatus } from '../types';
import { mapApiError } from '../utils/mapApiError';

const Rifas: React.FC = () => {
    const { token, user } = useAuth();
    const navigate = useNavigate();
    const [rifas, setRifas] = useState<Rifa[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchRifas();
    }, []);

    const fetchRifas = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/v1/rifas/', {
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

    if (loading) return <div className="p-5 text-gray-900 dark:text-gray-100">Carregando rifas...</div>;
    if (error) return <div className="p-5 text-red-600 dark:text-red-400">{error}</div>;

    return (
        <div className="p-5 max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-5">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Rifas Disponíveis</h1>
            </div>

            {rifas.length === 0 ? (
                <div className="p-10 text-center text-gray-500 bg-white dark:bg-gray-800 rounded-lg shadow">
                    <p>Nenhuma rifa disponível no momento.</p>
                </div>
            ) : (
                <div className="grid grid-cols-[repeat(auto-fill,minmax(300px,1fr))] gap-5">
                    {rifas.map((rifa) => (
                        <div key={rifa.id} className={`
                            bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border
                            ${rifa.status === RifaStatus.ATIVA ? 'border-green-500 dark:border-green-600' : 'border-gray-200 dark:border-gray-700'}
                        `}>
                            <div className={`
                                px-4 py-3 border-b
                                ${rifa.status === RifaStatus.ATIVA ? 'bg-green-50 dark:bg-green-900/20 border-green-100 dark:border-green-900/30' : 'bg-gray-50 dark:bg-gray-700 border-gray-100 dark:border-gray-600'}
                            `}>
                                <div className="flex justify-between">
                                    <span className={`
                                        font-bold uppercase text-xs
                                        ${rifa.status === RifaStatus.ATIVA ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400'}
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