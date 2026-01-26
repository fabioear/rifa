import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Clientes from './pages/Clientes';
import Rifas from './pages/Rifas';
import Sorteios from './pages/Sorteios';
import UsersPage from './pages/Users';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/clientes" element={<Clientes />} />
          <Route path="/rifas" element={<Rifas />} />
          <Route path="/sorteios" element={<Sorteios />} />
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['ADMIN', 'GLOBAL_ADMIN']} />}>
          <Route path="/users" element={<UsersPage />} />
        </Route>

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
