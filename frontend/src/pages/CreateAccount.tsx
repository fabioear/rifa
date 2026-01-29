import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { useTheme } from '../hooks/useTheme';
import { errorsPT } from '../i18n/errors.pt-BR';
import mascoteLogo from '../assets/mascotelogo.png';
import logoRifa from '../assets/logorifa.png';
import PasswordStrength from '../components/PasswordStrength';

const CreateAccount: React.FC = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [whatsappOptIn, setWhatsappOptIn] = useState(false);
    const [isPasswordValid, setIsPasswordValid] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [localError, setLocalError] = useState<string | null>(null);
    
    const { register, error } = useAuth();
    const navigate = useNavigate();
    const { mode, toggleTheme } = useTheme();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLocalError(null);
        
        if (password !== confirmPassword) {
            setLocalError(errorsPT.passwordsDontMatch);
            return;
        }

        if (!isPasswordValid) return;

        const success = await register(email, password, phone, whatsappOptIn);
        if (success) {
            navigate('/login');
        }
    };

    const isFormValid = 
        name.trim() !== '' && 
        email.trim() !== '' && 
        phone.trim() !== '' &&
        password !== '' && 
        confirmPassword !== '' &&
        password === confirmPassword &&
        isPasswordValid;

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
                    overflow-y: auto; /* Allow scrolling for taller forms */
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

                .login-card {
                    width: 100%;
                    max-width: 400px;
                    text-align: center;
                    margin: auto 0; /* Center vertically if possible */
                }

                .mascote-logo-img {
                    height: 100px; /* Smaller for register page */
                    object-fit: contain;
                    margin-bottom: 1rem;
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
                    margin-bottom: 1.5rem;
                }

                .input-group {
                    margin-bottom: 1rem;
                    text-align: left;
                }

                .input-group label {
                    display: block;
                    font-size: 0.875rem;
                    font-weight: 500;
                    margin-bottom: 0.4rem;
                    opacity: 0.9;
                }

                .input-field {
                    width: 100%;
                    padding: 10px 14px;
                    border-radius: 10px;
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
                .submit-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                [data-theme='light'] .submit-btn {
                    background: #0f172a;
                    color: #ffffff;
                }
                [data-theme='light'] .submit-btn:hover:not(:disabled) {
                    background: #1e293b;
                }

                [data-theme='dark'] .submit-btn {
                    background: linear-gradient(135deg, #00ffc8 0%, #00b4d8 100%);
                    color: #050814;
                    box-shadow: 0 4px 15px rgba(0, 255, 200, 0.3);
                }
                [data-theme='dark'] .submit-btn:hover:not(:disabled) {
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

                /* Checkbox Style */
                .checkbox-group {
                    display: flex;
                    align-items: center;
                    font-size: 0.85rem;
                    margin-bottom: 1rem;
                    text-align: left;
                }
                .checkbox-group input {
                    margin-right: 10px;
                    width: 16px;
                    height: 16px;
                    accent-color: #00ffc8;
                }
            `}</style>

            {/* Left Side: Full Screen Image */}
            <div className="login-image-section">
                <img src={logoRifa} alt="Império das Rifas" className="full-screen-image" />
            </div>

            {/* Right Side: Register Form */}
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
                    
                    <h1>Crie sua conta</h1>
                    <p className="subtitle">Preencha os dados abaixo para começar</p>

                    {(error || localError) && <div className="error-msg">{localError || error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="input-group">
                            <label>Nome completo</label>
                            <input 
                                type="text" 
                                className="input-field"
                                value={name} 
                                onChange={(e) => setName(e.target.value)} 
                                required 
                                placeholder="Seu nome"
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="email">Email</label>
                            <input
                                id="email"
                                type="email"
                                placeholder="seu@email.com"
                                className="input-field"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="phone">WhatsApp / Telefone</label>
                            <input
                                id="phone"
                                type="tel"
                                placeholder="(11) 99999-9999"
                                className="input-field"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                                required
                            />
                        </div>

                        <div className="input-group">
                            <label>Senha</label>
                            <div style={{ position: 'relative' }}>
                                <input 
                                    type={showPassword ? "text" : "password"}
                                    className="input-field"
                                    value={password} 
                                    onChange={(e) => setPassword(e.target.value)} 
                                    required 
                                    placeholder="Sua senha forte"
                                    style={{ paddingRight: '45px' }}
                                />
                                <button
                                    type="button"
                                    className="password-toggle-btn"
                                    onClick={() => setShowPassword(!showPassword)}
                                    tabIndex={-1}
                                >
                                    {showPassword ? (
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                                    ) : (
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8-11-8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                    )}
                                </button>
                            </div>
                            <div style={{ marginTop: '10px' }}>
                                <PasswordStrength password={password} onValidationChange={setIsPasswordValid} />
                            </div>
                        </div>

                        <div className="input-group">
                            <label>Confirmar Senha</label>
                            <div style={{ position: 'relative' }}>
                                <input 
                                    type={showConfirmPassword ? "text" : "password"}
                                    className={`input-field ${password !== confirmPassword && confirmPassword ? 'input-error' : ''}`}
                                    value={confirmPassword} 
                                    onChange={(e) => setConfirmPassword(e.target.value)} 
                                    required 
                                    placeholder="Repita sua senha"
                                    style={{ paddingRight: '45px' }}
                                />
                                <button
                                    type="button"
                                    className="password-toggle-btn"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    tabIndex={-1}
                                >
                                    {showConfirmPassword ? (
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                                    ) : (
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8-11-8-11-8-11-8-11-8-11-8-11-8-11-8-11-8-11-8-11-8-11-8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                    )}
                                </button>
                            </div>
                            {password !== confirmPassword && confirmPassword && (
                                <span className="error-message">{errorsPT.passwordsDontMatch}</span>
                            )}
                        </div>

                        <div className="checkbox-group">
                            <input
                                id="whatsapp-opt-in"
                                type="checkbox"
                                checked={whatsappOptIn}
                                onChange={(e) => setWhatsappOptIn(e.target.checked)}
                            />
                            <label htmlFor="whatsapp-opt-in">
                                Aceito receber notificações via WhatsApp
                            </label>
                        </div>

                        <button type="submit" className="submit-btn" disabled={!isFormValid}>
                            Criar Conta
                        </button>

                        <div className="login-link">
                            Já tem uma conta? <Link to="/login">Faça login</Link>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default CreateAccount;
