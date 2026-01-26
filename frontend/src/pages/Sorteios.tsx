import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import api from '../api/axios';
import { Loader2, Plus } from 'lucide-react';

interface Sorteio {
  id: number;
  rifa_id: number;
  numero_sorteio: number;
  descricao_premio: string;
  data_sorteio: string | null;
  ganhador_id: number | null;
}

interface Rifa {
  id: number;
  nome: string;
}

const Sorteios: React.FC = () => {
  const [sorteios, setSorteios] = useState<Sorteio[]>([]);
  const [rifas, setRifas] = useState<Rifa[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentSorteio, setCurrentSorteio] = useState<Partial<Sorteio>>({});

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [sorteiosRes, rifasRes] = await Promise.all([
        api.get('/sorteios/'),
        api.get('/rifas/')
      ]);
      setSorteios(sorteiosRes.data);
      setRifas(rifasRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Sorteios cannot be edited, only created
      await api.post('/sorteios/', currentSorteio);
      setIsModalOpen(false);
      setCurrentSorteio({});
      fetchData();
    } catch (err) {
      console.error("Failed to save sorteio", err);
      alert("Erro ao criar sorteio");
    }
  };

  const getRifaName = (id: number) => {
    const rifa = rifas.find(r => r.id === id);
    return rifa ? rifa.nome : `Rifa #${id}`;
  };

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Sorteios</h1>
        <button
          onClick={() => { setCurrentSorteio({}); setIsModalOpen(true); }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Novo Sorteio
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center p-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden transition-colors">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Rifa</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Prêmio</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Número</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Data Sorteio</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Ganhador</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {sorteios.map((sorteio) => (
                <tr key={sorteio.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{getRifaName(sorteio.rifa_id)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{sorteio.descricao_premio}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{sorteio.numero_sorteio}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {sorteio.data_sorteio ? new Date(sorteio.data_sorteio).toLocaleDateString() : '-'}
                  </td>
                   <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {sorteio.ganhador_id ? `Cliente #${sorteio.ganhador_id}` : 'Pendente'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Novo Sorteio</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
               <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Rifa</label>
                <select
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2"
                  value={currentSorteio.rifa_id || ''}
                  onChange={e => setCurrentSorteio({ ...currentSorteio, rifa_id: parseInt(e.target.value) })}
                >
                    <option value="">Selecione uma Rifa</option>
                    {rifas.map(rifa => (
                        <option key={rifa.id} value={rifa.id}>{rifa.nome}</option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Descrição do Prêmio</label>
                <input
                  type="text"
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2"
                  value={currentSorteio.descricao_premio || ''}
                  onChange={e => setCurrentSorteio({ ...currentSorteio, descricao_premio: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Número do Sorteio (Ordem)</label>
                <input
                  type="number"
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2"
                  value={currentSorteio.numero_sorteio || ''}
                  onChange={e => setCurrentSorteio({ ...currentSorteio, numero_sorteio: parseInt(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Data do Sorteio</label>
                <input
                  type="datetime-local"
                  className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2"
                  value={currentSorteio.data_sorteio ? String(currentSorteio.data_sorteio).slice(0, 16) : ''}
                  onChange={e => setCurrentSorteio({ ...currentSorteio, data_sorteio: e.target.value })}
                />
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-md"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
                >
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default Sorteios;
