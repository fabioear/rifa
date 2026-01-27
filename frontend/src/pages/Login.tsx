import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { useTheme } from '../hooks/useTheme';
import mascoteLogo from '../assets/mascotelogo.png';
import logoRifa from '../assets/logorifa.png';

const Login: React.FC = () => {
    const [email, setEmail] = useState('admin@example.com');
    const [password, setPassword] = useState('admin');
    const [showPassword, setShowPassword] = useState(false);
    const { login, error, isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const { mode, toggleTheme } = useTheme();

    // Redirect if already logged in
    React.useEffect(() => {
        if (isAuthenticated) {
            navigate('/rifas');
        }
    }, [isAuthenticated, navigate]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const success = await login(email, password);
        if (success) {
            navigate('/rifas');
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
                    background-color: #000; /* Fallback */
                }

                /* Left Side - Image (Fills remaining space) */
                .login-image-section {
                    display: none; /* Hidden on mobile */
                    position: relative;
                    flex: 1; /* Grow to fill all available space */
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

                /* Right Side - Form (Fixed width on desktop) */
                .login-form-section {
                    width: 100%; /* Mobile default */
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

                /* Desktop Layout */
                @media (min-width: 1024px) {
                    .login-image-section {
                        display: block;
                    }
                    .login-form-section {
                        width: 500px; /* Fixed width sidebar */
                        min-width: 500px;
                        flex-shrink: 0; /* Prevent shrinking */
                        box-shadow: -10px 0 30px rgba(0,0,0,0.15);
                    }
                }

                /* Theme Styles */
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

                /* Form Card Styles */
                .login-card {
                    width: 100%;
                    max-width: 400px;
                    text-align: center;
                }

                .mascote-logo-img {
                    display: block;
                    margin: 0 auto 1.5rem auto;
                    height: 140px;
                    object-fit: contain;
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

                /* Input Styles Light */
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

                /* Input Styles Dark */
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

                .password-toggle-btn {
                    position: absolute;
                    right: 12px;
                    top: 50%;
                    transform: translateY(-50%);
                    background: none;
                    border: none;
                    cursor: pointer;
                    opacity: 0.5;
                    color: inherit;
                    display: flex;
                    align-items: center;
                    padding: 4px;
                }
                .password-toggle-btn:hover {
                    opacity: 1;
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

                .error-msg {
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    font-size: 0.875rem;
                    text-align: left;
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
                
                [data-theme='dark'] .theme-toggle-fixed {
                    color: #fbbf24;
                }
                [data-theme='light'] .theme-toggle-fixed {
                    color: #0f172a;
                }
                .theme-toggle-fixed:hover {
                    background: rgba(128, 128, 128, 0.1);
                }

                .forgot-link {
                    font-size: 0.8rem;
                    opacity: 0.8;
                    text-decoration: none;
                    color: inherit;
                    float: right;
                    margin-top: 2px;
                }
                .forgot-link:hover {
                    text-decoration: underline;
                    opacity: 1;
                }
                
                .register-link {
                    margin-top: 1.5rem;
                    font-size: 0.9rem;
                    opacity: 0.8;
                }
                .register-link a {
                    color: inherit;
                    font-weight: 600;
                    text-decoration: none;
                }
                .register-link a:hover {
                    text-decoration: underline;
                }
            `}</style>

            {/* Left Side: Full Screen Image */}
            <div className="login-image-section">
                <img src={logoRifa} alt="Império das Rifas" className="full-screen-image" />
            </div>

            {/* Right Side: Login Form */}
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
                    
                    <h1>Bem-vindo</h1>
                    <p className="subtitle">Entre para gerenciar suas rifas</p>

                    {error && <div className="error-msg">{error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="input-group">
                            <label>Email</label>
                            <input 
                                type="email" 
                                className="input-field"
                                value={email} 
                                onChange={(e) => setEmail(e.target.value)} 
                                required 
                                placeholder="seu@email.com"
                            />
                        </div>
                        
                        <div className="input-group">
                            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem'}}>
                                <label style={{marginBottom: 0}}>Senha</label>
                                <Link to="/recuperar-senha" className="forgot-link">Esqueceu?</Link>
                            </div>
                            <div style={{ position: 'relative' }}>
                                <input 
                                    type={showPassword ? "text" : "password"}
                                    className="input-field"
                                    value={password} 
                                    onChange={(e) => setPassword(e.target.value)} 
                                    required 
                                    placeholder="••••••••"
                                    style={{ paddingRight: '45px' }}
                                />
                                <button
                                    type="button"
                                    className="password-toggle-btn"
                                    onClick={() => setShowPassword(!showPassword)}
                                    tabIndex={-1}
                                    title={showPassword ? "Ocultar senha" : "Mostrar senha"}
                                >
                                    {showPassword ? (
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                            <line x1="1" y1="1" x2="23" y2="23"></line>
                                        </svg>
                                    ) : (
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8-11-8-11-8-11-8-11-8z"></path>
                                            <circle cx="12" cy="12" r="3"></circle>
                                        </svg>
                                    )}
                                </button>
                            </div>
                        </div>

                        <button type="submit" className="submit-btn">
                            Entrar na Plataforma
                        </button>

                        <div className="register-link">
                            Não tem uma conta? <Link to="/cadastro">Cadastre-se</Link>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Login;
