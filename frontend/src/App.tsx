import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import CreateAccount from './pages/CreateAccount';
import ForgotPassword from './pages/ForgotPassword';
import Profile from './pages/Profile';
import Dashboard from './pages/Dashboard';
import Rifas from './pages/Rifas';
import RifaNumeros from './pages/RifaNumeros';
import AdminApuracao from './pages/AdminApuracao';
import AdminSorteios from './pages/AdminSorteios';
import AdminSettings from './pages/AdminSettings';
import MinhasCompras from './pages/MinhasCompras';
import HeroIllustration from './components/HeroIllustration';

// Simple placeholder for missing pages
const Placeholder: React.FC<{ title: string }> = ({ title }) => (
  <div className="p-8"><h1 className="text-2xl font-bold dark:text-white">{title}</h1><p className="dark:text-gray-300">Em construção...</p></div>
);

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/cadastro" element={<CreateAccount />} />
        <Route path="/recuperar-senha" element={<ForgotPassword />} />
        
        {/* Protected Routes */}
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/rifas" replace />} />
          <Route path="rifas" element={<Rifas />} />
          <Route path="rifas/:id" element={<RifaNumeros />} />
          <Route path="perfil" element={<Profile />} />
          
          {/* Admin Routes */}
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="admin-sorteios" element={<AdminSorteios />} />
          <Route path="admin-settings" element={<AdminSettings />} />
          <Route path="admin-apuracao" element={<AdminApuracao />} />
          <Route path="hero" element={<div style={{ height: '100vh' }}><HeroIllustration /></div>} />
          <Route path="usuarios" element={<Placeholder title="Gestão de Usuários" />} />
          
          <Route path="minhas-compras" element={<MinhasCompras />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
