import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useParams } from 'react-router-dom';
import { RifaNumero, NumeroStatus, Rifa } from '../types';
import { mapApiError } from '../utils/mapApiError';
import { getGrupoByNumero } from '../utils/jogoBichoData';

interface PaymentInfo {
    numero: string;
    payment_id: string;
    expires_at: string;
    qr_code?: string;
    qr_code_text?: string;
}

const RifaNumeros: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { token, user } = useAuth();
    
    const [numeros, setNumeros] = useState<RifaNumero[]>([]);
    const [rifa, setRifa] = useState<Rifa | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [filter, setFilter] = useState('');
    const [paymentInfo, setPaymentInfo] = useState<PaymentInfo | null>(null);

    const formatNumero = (num: string, tipo?: string) => {
        if (!tipo) return num;
        if (tipo === 'dezena' && num === '100') return '00';
        if (tipo === 'centena' && num === '1000') return '000';
        if (tipo === 'milhar' && num === '10000') return '0000';
        return num;
    };

    useEffect(() => {
        if (id) {
            fetchRifaAndNumeros();
        } else {
            setLoading(false);
            setError("ID da rifa não fornecido.");
        }
    }, [id]);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (paymentInfo) {
            interval = setInterval(() => {
                const now = new Date();
                const expiresAt = new Date(paymentInfo.expires_at);
                if (now > expiresAt) {
                    setError("Tempo de reserva expirado! O número foi liberado.");
                    setPaymentInfo(null);
                    fetchRifaAndNumeros();
                    setTimeout(() => setError(null), 5000);
                }
            }, 1000);
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [paymentInfo]);

    const fetchRifaAndNumeros = async () => {
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            const [rifaRes, numerosRes] = await Promise.all([
                axios.get(`${apiUrl}/rifas/${id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                axios.get(`${apiUrl}/rifas/${id}/numeros`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);
            setRifa(rifaRes.data);
            setNumeros(numerosRes.data);
        } catch (err) {
            setError(mapApiError(err));
        } finally {
            setLoading(false);
        }
    };

    const handleReserve = async (numero: string) => {
        setError(null);
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            // 1. Reserve Number
            const reserveRes = await axios.post(
                `${apiUrl}/rifas/${id}/numeros/${numero}/reservar`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // 2. Get PIX Payment Details
            const paymentRes = await axios.post(
                `${apiUrl}/pagamentos/pix`,
                { payment_id: reserveRes.data.payment_id },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            setPaymentInfo({
                numero: numero,
                payment_id: reserveRes.data.payment_id,
                expires_at: reserveRes.data.expires_at,
                qr_code: paymentRes.data.qr_code,
                qr_code_text: paymentRes.data.pix_code
            });
            
            // Refresh list
            fetchRifaAndNumeros();
            
        } catch (err: any) {
            setError(mapApiError(err));
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setSuccessMessage("Copiado para a área de transferência!");
        setTimeout(() => setSuccessMessage(null), 3000);
    };

    if (loading) return <div className="p-5 text-gray-900 dark:text-gray-100">Carregando...</div>;
    if (!rifa) return <div className="p-5 text-gray-900 dark:text-gray-100">Rifa não encontrada</div>;

    const isGrupo = rifa.tipo_rifa === 'grupo';
    const gridClass = isGrupo 
        ? "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
        : "grid grid-cols-[repeat(auto-fill,minmax(80px,1fr))] gap-2.5";

    // Use glob import to ensure Vite bundles the assets correctly
    const groupImages = import.meta.glob('../assets/grupos/*.png', { eager: true });

    const getImageUrl = (imageName: string) => {
        const key = `../assets/grupos/${imageName}`;
        const mod = groupImages[key] as { default: string };
        return mod?.default || '';
    };

    return (
        <div className="p-5 max-w-7xl mx-auto">
            <h2 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">{rifa.titulo} - Escolha seus números</h2>
            <div className="flex flex-col sm:flex-row gap-4 mb-4 text-gray-600 dark:text-gray-400">
                <span>Tipo: {rifa.tipo_rifa}</span>
                <span className="hidden sm:inline">|</span>
                <span>Sorteio: {new Date(rifa.data_sorteio).toLocaleString()}</span>
                {rifa.valor_premio && (
                    <>
                        <span className="hidden sm:inline">|</span>
                        <span className="font-semibold text-green-600 dark:text-green-400">
                            Prêmio: R$ {rifa.valor_premio.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </span>
                    </>
                )}
            </div>
            
            {(error || successMessage) && (
                <div className={`mb-4 p-4 rounded-md ${
                    error 
                        ? 'bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30' 
                        : 'bg-green-50 text-green-700 border border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30'
                }`}>
                    {error || successMessage}
                </div>
            )}

            <div className="mb-5">
                <input 
                    type="text" 
                    placeholder="Filtrar número..." 
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="w-full max-w-xs px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 dark:text-white"
                />
            </div>

            <div className={gridClass}>
                {numeros
                    .filter(n => n.numero.includes(filter))
                    .map((num) => {
                        const isMyNumber = num.is_owner || num.user_id === user?.id;
                        const isLivre = num.status === NumeroStatus.LIVRE || num.status === NumeroStatus.EXPIRADO;
                        const isReservado = num.status === NumeroStatus.RESERVADO;
                        const isPago = num.status === NumeroStatus.PAGO;
                        const isCancelado = num.status === NumeroStatus.CANCELADO;
                        
                        let bgClass = 'bg-white dark:bg-gray-800';
                        let textClass = 'text-gray-900 dark:text-gray-100';
                        let cursorClass = 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700';
                        let borderClass = 'border-gray-300 dark:border-gray-600';
                        let label = formatNumero(num.numero, rifa?.tipo_rifa);

                        if (isPago) {
                            bgClass = 'bg-green-500 dark:bg-green-600';
                            textClass = 'text-white';
                            cursorClass = 'cursor-not-allowed';
                            borderClass = 'border-green-600';
                        } else if (isCancelado) {
                             bgClass = 'bg-red-500 dark:bg-red-600';
                             textClass = 'text-white';
                             cursorClass = 'cursor-not-allowed';
                             borderClass = 'border-red-600';
                        } else if (isReservado) {
                            if (isMyNumber) {
                                bgClass = 'bg-red-500 dark:bg-red-600';
                                textClass = 'text-white';
                                label += ' (Pagar)';
                            } else {
                                bgClass = 'bg-gray-500 dark:bg-gray-600';
                                textClass = 'text-white';
                                cursorClass = 'cursor-not-allowed';
                                borderClass = 'border-gray-600';
                            }
                        }

                        // Jogo do Bicho Card Content
                        let cardContent = <>{label}</>;
                        if (isGrupo) {
                            const grupoData = getGrupoByNumero(num.numero);
                            if (grupoData) {
                                cardContent = (
                                    <div className="flex flex-col items-center">
                                        <div className="text-xs uppercase mb-1">{grupoData.nome}</div>
                                        <img 
                                            src={getImageUrl(grupoData.imagem)} 
                                            alt={grupoData.nome}
                                            className="w-16 h-16 object-contain mb-1"
                                        />
                                        <div className="text-lg font-bold">Grupo {grupoData.id}</div>
                                        <div className="text-xs mt-1">
                                            {grupoData.dezenas.join(' - ')}
                                        </div>
                                    </div>
                                );
                            }
                        }

                        return (
                            <div 
                                key={num.id}
                                onClick={() => {
                                    if (isLivre || (isReservado && isMyNumber)) {
                                        handleReserve(num.numero);
                                    }
                                }}
                                className={`
                                    border rounded-md p-2.5 text-center font-bold transition-colors
                                    ${bgClass} ${textClass} ${cursorClass} ${borderClass}
                                    ${isGrupo ? 'h-auto min-h-[140px]' : ''}
                                `}
                            >
                                {cardContent}
                            </div>
                        );
                    })}
            </div>

            {/* Payment Modal Overlay */}
            {paymentInfo && (
                <div 
                    className="fixed inset-0 flex justify-center items-center z-[9999] px-4"
                    style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
                >
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg max-w-md w-full shadow-xl relative">
                        <button
                            onClick={() => setPaymentInfo(null)}
                            className="absolute top-4 right-4 text-gray-400 hover:text-gray-500 focus:outline-none"
                        >
                            <span className="sr-only">Fechar</span>
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Pagamento - Número {paymentInfo.numero}</h3>
                        <p className="text-gray-500 dark:text-gray-400 mb-4">Realize o pagamento para confirmar sua reserva.</p>
                        
                        {paymentInfo.qr_code && (
                            <div className="flex justify-center mb-4">
                                <img src={`data:image/png;base64,${paymentInfo.qr_code}`} alt="QR Code PIX" className="max-w-[200px]" />
                            </div>
                        )}
                        
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Código PIX Copia e Cola</label>
                            <div className="flex gap-2">
                                <input 
                                    type="text" 
                                    readOnly 
                                    value={paymentInfo.qr_code_text || ''}
                                    className="flex-1 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-700 dark:text-white"
                                />
                                <button 
                                    onClick={() => copyToClipboard(paymentInfo.qr_code_text || '')}
                                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                >
                                    Copiar
                                </button>
                            </div>
                        </div>
                        
                        <div className="mt-5 sm:mt-6">
                            <button
                                type="button"
                                onClick={() => setPaymentInfo(null)}
                                className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
                            >
                                Fechar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RifaNumeros;