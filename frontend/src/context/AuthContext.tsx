import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { mapApiError } from '../utils/mapApiError';
import { useTheme } from '../hooks/useTheme';

interface User {
    id: string;
    role: 'admin' | 'player';
    email?: string;
    sub?: string;
    name?: string;
    avatar_url?: string | null;
}

interface AuthContextType {
    token: string | null;
    user: User | null;
    login: (email: string, password: string) => Promise<boolean>;
    register: (email: string, password: string, name: string, phone?: string, whatsappOptIn?: boolean) => Promise<boolean>;
    logout: () => void;
    error: string | null;
    isAuthenticated: boolean;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function parseJwt(token: string): User | null {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        const decoded = JSON.parse(jsonPayload);
        
        // Map JWT claims to User object
        return {
            id: decoded.sub || '',
            role: decoded.role || 'player',
            email: decoded.email
        };
    } catch (e) {
        return null;
    }
}

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
    // Initialize user synchronously from token, then we'll fetch details
    const [user, setUser] = useState<User | null>(() => {
        const t = localStorage.getItem('access_token');
        return t ? parseJwt(t) : null;
    });
    const [error, setError] = useState<string | null>(null);
    const { setTheme } = useTheme();

    // Function to fetch full user details
    const refreshUser = async () => {
        const currentToken = localStorage.getItem('access_token');
        if (!currentToken) return;

        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            const response = await axios.get(`${apiUrl}/users/me`, {
                headers: { Authorization: `Bearer ${currentToken}` }
            });
            
            if (response.data) {
                setUser(prev => ({
                    ...prev,
                    ...response.data, // Merge API data (including avatar_url)
                    id: prev?.id || response.data.id,
                    role: prev?.role || response.data.role
                }));
            }
        } catch (err) {
            console.error("Failed to refresh user data", err);
            // Don't logout here, just keep using token data if API fails temporarily
        }
    };

    // Intercept 401 responses to auto-logout
    useEffect(() => {
        const interceptor = axios.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401) {
                    setToken(null);
                    localStorage.removeItem('access_token');
                    setUser(null);
                }
                return Promise.reject(error);
            }
        );
        return () => {
            axios.interceptors.response.eject(interceptor);
        };
    }, []);

    useEffect(() => {
        if (token) {
            const userData = parseJwt(token);
            if (userData) {
                setUser(userData);
                // Fetch full details (avatar, name, etc.)
                refreshUser();
            } else {
                // Invalid token
                logout();
            }
        } else {
            setUser(null);
        }
    }, [token]);

    const login = async (email: string, password: string) => {
        setError(null);
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            const response = await axios.post(`${apiUrl}/login/access-token`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            const accessToken = response.data.access_token;
            setToken(accessToken);
            localStorage.setItem('access_token', accessToken);
            
            // Check for theme preference in response (if backend supports it)
            if (response.data.theme) {
                setTheme(response.data.theme);
            }

            // User will be set by useEffect
            return true;
        } catch (err: any) {
            console.error("Login error:", err);
            setError(mapApiError(err));
            return false;
        }
    };

    const register = async (email: string, password: string, name: string, phone?: string, whatsappOptIn?: boolean) => {
        setError(null);
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
            await axios.post(`${apiUrl}/users`, {
                email,
                password,
                name,
                phone,
                whatsapp_opt_in: whatsappOptIn
            });
            // Auto login after register or redirect to login? 
            // For now, let's just return true and let UI decide (usually redirect to login)
            return true;
        } catch (err: any) {
            console.error("Register error:", err);
            setError(mapApiError(err));
            return false;
        }
    };

    const logout = () => {
        setToken(null);
        localStorage.removeItem('access_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ token, user, login, register, logout, error, isAuthenticated: !!user, refreshUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
