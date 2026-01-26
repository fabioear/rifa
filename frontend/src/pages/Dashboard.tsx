import React from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <Layout>
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 transition-colors duration-200">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Bem-vindo, {user?.nome}!
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800">
            <h3 className="text-lg font-medium text-blue-800 dark:text-blue-300">Tenant Atual</h3>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-2">
              {user?.role === 'global_admin' ? 'Global Admin (All)' : `Tenant #${user?.tenant_id}`}
            </p>
          </div>
          {/* Add more stats widgets here */}
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-100 dark:border-green-800">
            <h3 className="text-lg font-medium text-green-800 dark:text-green-300">Status</h3>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-2">Ativo</p>
          </div>
           <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-100 dark:border-purple-800">
            <h3 className="text-lg font-medium text-purple-800 dark:text-purple-300">Role</h3>
            <p className="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-2 capitalize">{user?.role?.replace('_', ' ')}</p>
          </div>
        </div>
        
        <div className="mt-8">
            <p className="text-gray-600 dark:text-gray-400">
                Selecione uma opção no menu lateral para gerenciar Clientes, Rifas ou Sorteios.
            </p>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
