import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../hooks/useTheme';
import { errorsPT } from '../i18n/errors.pt-BR';
import mascoteLogo from '../assets/mascotelogo.png';
import logoRifa from '../assets/logorifa.png';
import { mapApiError } from '../utils/mapApiError';

const ForgotPassword: React.FC = () => {
    const [email, setEmail] = useState('');
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { mode, toggleTheme } = useTheme();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        
        if (!email) {
            setError(errorsPT.required);
            return;
        }

        // Mock API call to request password reset
        try {
            // await axios.post('/api/v1/auth/forgot-password', { email });
            // For now, simulate success
            setSubmitted(true);
        } catch (err: any) {
            setError(mapApiError(err));
        }
    };

    return (
        <div className="login-container">
            <style>{`
                .login-container {
                    display: flex;
                    height: 100vh;
                    width: 100%;
                    overflow: hidden;
                    background-color: #000;
                }

                .login-image-section {
                    display: none;
                    position: relative;
                    flex: 1;
                    overflow: hidden;
                }

                .full-screen-image {
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    display: block;
                    padding: 2rem;
                    box-sizing: border-box;
                }

                .login-form-section {
                    width: 100%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 2rem;
                    position: relative;
                    transition: background 0.3s ease;
                    z-index: 20;
                    box-sizing: border-box;
                }

                @media (min-width: 1024px) {
                    .login-image-section {
                        display: block;
                    }
                    .login-form-section {
                        width: 500px;
                        min-width: 500px;
                        flex-shrink: 0;
                        box-shadow: -10px 0 30px rgba(0,0,0,0.15);
                    }
                }

                [data-theme='dark'] .login-form-section {
                    background: linear-gradient(to bottom, #050814, #0a0f2c);
                    color: #f8fafc;
                }
                
                [data-theme='dark'] .login-image-section {
                    background: linear-gradient(to bottom, #050814, #0a0f2c);
                }

                [data-theme='light'] .login-form-section {
                    background: #ffffff;
                    color: #0f172a;
                }

                [data-theme='light'] .error-msg {
                    background: #fef2f2;
                    color: #dc2626; /* red-600 */
                    border: 1px solid #fee2e2;
                }
                [data-theme='dark'] .error-msg {
                    background: rgba(220, 38, 38, 0.1);
                    color: #f87171; /* red-400 */
                    border: 1px solid rgba(248, 113, 113, 0.2);
                }

                .login-card {
                    width: 100%;
                    max-width: 400px;
                    text-align: center;
                }

                .mascote-logo-img {
                    height: 140px;
                    object-fit: contain;
                    margin-bottom: 1.5rem;
                    filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1));
                    animation: float 6s ease-in-out infinite;
                }

                @keyframes float {
                    0% { transform: translateY(0px); }
                    50% { transform: translateY(-10px); }
                    100% { transform: translateY(0px); }
                }

                h1 {
                    font-size: 1.75rem;
                    font-weight: 700;
                    margin-bottom: 0.5rem;
                }

                p.subtitle {
                    font-size: 0.9rem;
                    opacity: 0.7;
                    margin-bottom: 2rem;
                }

                .input-group {
                    margin-bottom: 1.25rem;
                    text-align: left;
                }

                .input-group label {
                    display: block;
                    font-size: 0.875rem;
                    font-weight: 500;
                    margin-bottom: 0.5rem;
                    opacity: 0.9;
                }

                .input-field {
                    width: 100%;
                    padding: 12px 16px;
                    border-radius: 12px;
                    font-size: 0.95rem;
                    transition: all 0.2s;
                    box-sizing: border-box;
                }

                [data-theme='light'] .input-field {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    color: #0f172a;
                }
                [data-theme='light'] .input-field:focus {
                    background: #ffffff;
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                    outline: none;
                }

                [data-theme='dark'] .input-field {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    color: #f8fafc;
                }
                [data-theme='dark'] .input-field:focus {
                    background: rgba(255, 255, 255, 0.05);
                    border-color: #00ffc8;
                    box-shadow: 0 0 0 3px rgba(0, 255, 200, 0.1);
                    outline: none;
                }

                .submit-btn {
                    width: 100%;
                    padding: 14px;
                    border-radius: 12px;
                    border: none;
                    font-weight: 600;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: all 0.2s;
                    margin-top: 1rem;
                }

                [data-theme='light'] .submit-btn {
                    background: #0f172a;
                    color: #ffffff;
                }
                [data-theme='light'] .submit-btn:hover {
                    background: #1e293b;
                }

                [data-theme='dark'] .submit-btn {
                    background: linear-gradient(135deg, #00ffc8 0%, #00b4d8 100%);
                    color: #050814;
                    box-shadow: 0 4px 15px rgba(0, 255, 200, 0.3);
                }
                [data-theme='dark'] .submit-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(0, 255, 200, 0.4);
                }

                .theme-toggle-fixed {
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background: none;
                    border: none;
                    cursor: pointer;
                    font-size: 1.5rem;
                    padding: 8px;
                    border-radius: 50%;
                    transition: background 0.2s;
                    z-index: 30;
                }
                [data-theme='dark'] .theme-toggle-fixed { color: #fbbf24; }
                [data-theme='light'] .theme-toggle-fixed { color: #0f172a; }
                .theme-toggle-fixed:hover { background: rgba(128, 128, 128, 0.1); }

                .login-link {
                    margin-top: 1.5rem;
                    font-size: 0.9rem;
                    opacity: 0.8;
                }
                .login-link a {
                    color: inherit;
                    font-weight: 600;
                    text-decoration: none;
                }
                .login-link a:hover {
                    text-decoration: underline;
                }

                .success-box {
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    color: #10b981;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-top: 1rem;
                    text-align: left;
                    font-size: 0.9rem;
                }
            `}</style>

            {/* Left Side: Full Screen Image */}
            <div className="login-image-section">
                <img src={logoRifa} alt="Império das Rifas" className="full-screen-image" />
            </div>

            {/* Right Side: Forgot Password Form */}
            <div className="login-form-section">
                <button 
                    onClick={toggleTheme} 
                    className="theme-toggle-fixed"
                    title={mode === 'dark' ? 'Mudar para Light Mode' : 'Mudar para Dark Mode'}
                >
                    {mode === 'dark' ? '☀️' : '🌙'}
                </button>

                <div className="login-card">
                    <img src={mascoteLogo} alt="Mascote Logo" className="mascote-logo-img" />
                    
                    <h1>Recuperar Senha</h1>
                    <p className="subtitle">Digite seu e-mail para receber as instruções</p>

                    {error && <div className="error-msg">{error}</div>}

                    {!submitted ? (
                        <form onSubmit={handleSubmit}>
                            <div className="input-group">
                                <label>E-mail cadastrado</label>
                                <input 
                                    type="email" 
                                    className="input-field"
                                    value={email} 
                                    onChange={(e) => setEmail(e.target.value)} 
                                    required 
                                    placeholder="seu@email.com"
                                />
                            </div>

                            <button type="submit" className="submit-btn">
                                Enviar instruções
                            </button>
                        </form>
                    ) : (
                        <div className="success-box">
                            <strong>Solicitação enviada!</strong>
                            <p style={{ marginTop: '0.5rem', opacity: 0.9 }}>
                                Se este e-mail existir em nossa base, enviaremos as instruções para redefinir sua senha em instantes.
                            </p>
                        </div>
                    )}

                    <div className="login-link">
                        <Link to="/login">Voltar para o Login</Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ForgotPassword;
