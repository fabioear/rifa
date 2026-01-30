import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Winner {
    user_name: string;
    avatar_url: string | null;
    rifa_title: string;
    numero: string;
    data_ganho: string;
}

const getInitials = (name: string) => {
    if (!name) return '??';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

const WinnerItem = ({ winner }: { winner: Winner }) => {
    const apiUrl = import.meta.env.VITE_API_URL || '';
    // Remove /api/v1 suffix if present for static file serving base URL
    const cleanApiUrl = apiUrl.replace(/\/api\/v1\/?$/, '');
    
    // Construct full image URL
    let imageUrl: string | null = null;
    if (winner.avatar_url) {
        if (winner.avatar_url.startsWith('http')) {
            imageUrl = winner.avatar_url;
        } else {
            // Ensure we don't double slash
            const prefix = cleanApiUrl.endsWith('/') ? cleanApiUrl.slice(0, -1) : cleanApiUrl;
            const path = winner.avatar_url.startsWith('/') ? winner.avatar_url : `/${winner.avatar_url}`;
            imageUrl = `${prefix}${path}`;
        }
    }
    
    // State to handle image error
    const [imgError, setImgError] = useState(false);

    return (
        <div className="flex items-center space-x-3 bg-white/10 rounded-full px-4 py-1.5 backdrop-blur-sm border border-white/20 min-w-max">
            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-white text-yellow-600 flex items-center justify-center font-bold text-xs overflow-hidden border-2 border-yellow-200">
                {imageUrl && !imgError ? (
                    <img 
                        src={imageUrl} 
                        alt={winner.user_name} 
                        className="h-full w-full object-cover"
                        onError={() => setImgError(true)}
                    />
                ) : (
                    <span>{getInitials(winner.user_name)}</span>
                )}
            </div>
            <div className="flex flex-col text-xs text-white leading-tight">
                <span className="font-bold">{winner.user_name}</span>
                <span className="opacity-90">Ganhou <span className="text-yellow-100 font-bold">#{winner.numero}</span> em {winner.rifa_title}</span>
            </div>
        </div>
    );
};

export const WinnersBar = () => {
    const [winners, setWinners] = useState<Winner[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchWinners = async () => {
            try {
                const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
                // Adjust if VITE_API_URL doesn't include /api/v1 (it usually does in this project context based on auth.py usage)
                // But let's be safe: if the env var ends with /api/v1, use it, else append.
                // In Profile.tsx user used `import.meta.env.VITE_API_URL || '/api/v1'`, implying VITE_API_URL is the full path or relative.
                // Let's assume axios baseURL is configured or we use full path.
                
                const response = await axios.get(`${apiUrl}/rifas/recent-winners?limit=10`);
                setWinners(response.data);
            } catch (error) {
                console.error("Erro ao buscar ganhadores:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchWinners();
    }, []);

    if (loading || winners.length === 0) return null;

    return (
        <div className="bg-gradient-to-r from-yellow-600 via-amber-500 to-yellow-600 text-white py-2 overflow-hidden relative shadow-md z-10 border-b border-yellow-400 w-full">
            <div className="flex animate-marquee hover:[animation-play-state:paused] whitespace-nowrap">
                <div className="flex space-x-8 px-4 items-center">
                    {winners.map((winner, idx) => (
                        <WinnerItem key={idx} winner={winner} />
                    ))}
                </div>
                {/* Duplicate for infinite loop - ensure enough content to scroll */}
                <div className="flex space-x-8 px-4 ml-8 items-center">
                    {winners.map((winner, idx) => (
                        <WinnerItem key={`dup-${idx}`} winner={winner} />
                    ))}
                </div>
            </div>
        </div>
    );
};
