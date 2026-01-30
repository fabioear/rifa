import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Rifa, RifaStatus, RifaTipo, RifaLocal, Sorteio } from '../types';
import { mapApiError } from '../utils/mapApiError';
import CurrencyInput from '../components/ui/CurrencyInput';

const Dashboard: React.FC = () => {
    const { token } = useAuth();
    const [rifas, setRifas] = useState<Rifa[]>([]);
    const [loading, setLoading] = useState(true);
    
    // Form State
    const [showForm, setShowForm] = useState(false);
    const [newRifa, setNewRifa] = useState({
        titulo: '',
        descricao: '',
        preco_numero: '',
        valor_premio: '',
        tipo_rifa: RifaTipo.MILHAR,
        local_sorteio: '',
        data_sorteio: '',
        hora_encerramento: '',
        status: RifaStatus.RASCUNHO,
        quantidade_numeros: 0
    });

    // Sorteios State
    const [sorteios, setSorteios] = useState<Sorteio[]>([]);

    // Admin Settings State
    const [fechamentoMinutos, setFechamentoMinutos] = useState(20);

    useEffect(() => {
        fetchData();
        fetchSorteios();
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            // Assuming we have an endpoint for settings or we can get it. 
            // For now, let's try to get it from a new endpoint or default.
            // Wait, we need to create the endpoint first.
            // Let's assume we will create /api/v1/admin/settings
             const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
             const response = await axios.get(`${apiUrl}/admin/settings`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.data && response.data.fechamento_minutos) {
                setFechamentoMinutos(response.data.fechamento_minutos);
            }
        } catch (err) {
            console.error("Erro ao carregar configurações:", err);
        }
    };

    const fetchSorteios = async () => {
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            const response = await axios.get(`${apiUrl}/sorteios/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setSorteios(response.data);
        } catch (err) {
            console.error("Erro ao carregar sorteios:", err);
        }
    };

    const fetchData = async () => {
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            const response = await axios.get(`${apiUrl}/rifas/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setRifas(response.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSorteioChange = (nome: string) => {
        const selectedSorteio = sorteios.find(s => s.nome === nome);
        
        let newDataSorteio = newRifa.data_sorteio;
        let newHoraEncerramento = newRifa.hora_encerramento;

        // If we have a date selected (or default to today if empty)
        let dateBase = newDataSorteio ? newDataSorteio.split('T')[0] : new Date().toISOString().split('T')[0];

        if (selectedSorteio) {
            // Update data_sorteio time
            if (selectedSorteio.horario) {
                // Ensure HH:MM format
                const time = selectedSorteio.horario.substring(0, 5); 
                newDataSorteio = `${dateBase}T${time}`;

                // Calculate hora_encerramento based on global setting
                // Parse hours and minutes
                const [hours, minutes] = time.split(':').map(Number);
                const date = new Date(dateBase);
                date.setHours(hours);
                date.setMinutes(minutes);
                
                // Subtract minutes
                date.setMinutes(date.getMinutes() - fechamentoMinutos);
                
                // Format back to HH:MM
                const encHours = String(date.getHours()).padStart(2, '0');
                const encMinutes = String(date.getMinutes()).padStart(2, '0');
                newHoraEncerramento = `${dateBase}T${encHours}:${encMinutes}`;
            }
        }
        
        setNewRifa({
            ...newRifa, 
            local_sorteio: nome,
            data_sorteio: newDataSorteio,
            hora_encerramento: newHoraEncerramento
        });
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            // Determine quantidade_numeros based on tipo
            let qtd = 0;
            if (newRifa.tipo_rifa === RifaTipo.MILHAR) qtd = 10000;
            else if (newRifa.tipo_rifa === RifaTipo.CENTENA) qtd = 1000;
            else if (newRifa.tipo_rifa === RifaTipo.DEZENA) qtd = 100;
            else if (newRifa.tipo_rifa === RifaTipo.GRUPO) qtd = 25;

            const payload = {
                ...newRifa,
                preco_numero: parseFloat(newRifa.preco_numero),
                valor_premio: newRifa.valor_premio ? parseFloat(newRifa.valor_premio) : null,
                quantidade_numeros: qtd,
                // If data_sorteio is provided, ensure it has timezone or is valid ISO
                data_sorteio: new Date(newRifa.data_sorteio).toISOString(),
                hora_encerramento: newRifa.hora_encerramento ? new Date(newRifa.hora_encerramento).toISOString() : null
            };

            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            await axios.post(`${apiUrl}/rifas/`, payload, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setShowForm(false);
            setNewRifa({ 
                titulo: '', 
                descricao: '', 
                preco_numero: '', 
                valor_premio: '',
                tipo_rifa: RifaTipo.MILHAR,
                local_sorteio: '',
                data_sorteio: '',
                hora_encerramento: '',
                status: RifaStatus.RASCUNHO,
                quantidade_numeros: 0
            });
            fetchData(); // Refresh list
            alert('Rifa criada com sucesso!');
        } catch (err) {
            console.error(err);
            alert(mapApiError(err));
        }
    };

    const handleStatusChange = async (id: string, newStatus: string) => {
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            await axios.patch(`${apiUrl}/rifas/${id}/status`, 
                { status: newStatus },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            fetchData();
        } catch (err) {
            console.error(err);
            alert(mapApiError(err));
        }
    };

    const generateWhatsAppText = (rifa: Rifa) => {
        const dataSorteio = new Date(rifa.data_sorteio).toLocaleDateString('pt-BR');
        return `🎰 Nova rifa disponível no Império das Rifas!
Rifa: ${rifa.titulo}
Sorteio: ${dataSorteio}
Tipo: ${rifa.tipo_rifa}
Participe de forma simples e rápida. Confira os detalhes e jogue pelo site oficial:
👉 https://imperiodasrifas.app.br/rifa/${rifa.id}`;
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text).then(() => {
            alert('Texto copiado para o WhatsApp!');
        }, (err) => {
            console.error('Erro ao copiar: ', err);
            alert('Erro ao copiar texto.');
        });
    };

    if (loading) return <div className="p-5 text-gray-900 dark:text-gray-100">Carregando...</div>;

    return (
        <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard Administrativo</h1>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">Gerencie suas rifas e acompanhe vendas.</p>
                </div>
                <button 
                    onClick={() => setShowForm(!showForm)}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors font-medium shadow-sm"
                >
                    {showForm ? 'Cancelar' : '+ Nova Rifa'}
                </button>
            </div>

            {/* Create Form */}
            {showForm && (
                <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-md mb-8 border border-gray-200 dark:border-slate-700">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Criar Nova Rifa</h3>
                    <form onSubmit={handleCreate} className="grid gap-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Título</label>
                                <input 
                                    type="text" 
                                    value={newRifa.titulo}
                                    onChange={e => setNewRifa({...newRifa, titulo: e.target.value})}
                                    required
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Preço Número (R$)</label>
                                <CurrencyInput 
                                    value={newRifa.preco_numero}
                                    onChange={val => setNewRifa({...newRifa, preco_numero: val})}
                                    required
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Valor do Prêmio (R$)</label>
                            <CurrencyInput 
                                value={newRifa.valor_premio}
                                onChange={val => setNewRifa({...newRifa, valor_premio: val})}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Descrição</label>
                            <textarea 
                                value={newRifa.descricao}
                                onChange={e => setNewRifa({...newRifa, descricao: e.target.value})}
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                             <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tipo de Rifa</label>
                                <select 
                                    value={newRifa.tipo_rifa}
                                    onChange={e => setNewRifa({...newRifa, tipo_rifa: e.target.value as RifaTipo})}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                                >
                                    {Object.values(RifaTipo).map(t => (
                                        <option key={t} value={t}>{t.toUpperCase()}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Local Sorteio</label>
                                <select 
                                    value={newRifa.local_sorteio}
                                    onChange={e => handleSorteioChange(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                                >
                                    <option value="">Selecione um local</option>
                                    {sorteios.map(s => (
                                        <option key={s.id} value={s.nome}>{s.nome}</option>
                                    ))}
                                    {sorteios.length === 0 && Object.values(RifaLocal).map(l => (
                                        <option key={l} value={l}>{l}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                         <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Data Sorteio</label>
                                <input 
                                    type="datetime-local" 
                                    value={newRifa.data_sorteio}
                                    onChange={e => setNewRifa({...newRifa, data_sorteio: e.target.value})}
                                    required
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Hora Encerramento (Opcional)</label>
                                <input 
                                    type="datetime-local" 
                                    value={newRifa.hora_encerramento}
                                    onChange={e => setNewRifa({...newRifa, hora_encerramento: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                                />
                            </div>
                        </div>

                        <button 
                            type="submit" 
                            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                        >
                            Criar Rifa
                        </button>
                    </form>
                </div>
            )}

            {/* List */}
            <div className="bg-white dark:bg-slate-800 shadow overflow-hidden rounded-lg border border-gray-200 dark:border-slate-700">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
                    <thead className="bg-gray-50 dark:bg-slate-700">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Título
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Tipo
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Preço
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Prêmio
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Status
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Ações
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-slate-800 divide-y divide-gray-200 dark:divide-slate-700">
                        {rifas.map(rifa => (
                            <tr key={rifa.id} className="hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                                    {rifa.titulo}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                    {rifa.tipo_rifa}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                    R$ {rifa.preco_numero.toFixed(2)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                    {rifa.valor_premio ? `R$ ${rifa.valor_premio.toFixed(2)}` : '-'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                        ${rifa.status === RifaStatus.ATIVA ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : ''}
                                        ${rifa.status === RifaStatus.RASCUNHO ? 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300' : ''}
                                        ${rifa.status === RifaStatus.ENCERRADA ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' : ''}
                                    `}>
                                        {rifa.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                                    {rifa.status === RifaStatus.RASCUNHO && (
                                        <button 
                                            onClick={() => handleStatusChange(rifa.id, RifaStatus.ATIVA)}
                                            className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                                        >
                                            Ativar
                                        </button>
                                    )}
                                    {rifa.status === RifaStatus.ATIVA && (
                                        <button 
                                            onClick={() => handleStatusChange(rifa.id, RifaStatus.ENCERRADA)}
                                            className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                                        >
                                            Encerrar
                                        </button>
                                    )}
                                    <button 
                                        onClick={() => copyToClipboard(generateWhatsAppText(rifa))}
                                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                                        title="Copiar texto para WhatsApp"
                                    >
                                        Zap
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Dashboard;