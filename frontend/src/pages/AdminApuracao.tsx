import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { Rifa, RifaStatus, RifaTipo } from "../types";
import { mapApiError } from "../utils/mapApiError";

interface RifaResumo {
  rifa_id: string;
  titulo: string;
  status: string;
  total_arrecadado: number;
  total_numeros_pagos: number;
  resultado_lancado: boolean;
  resultado?: {
    valor: string | null;
    local_sorteio: string | null;
    data_resultado: string | null;
    apurado: boolean;
  } | null;
  quantidade_ganhadores: number;
}

interface GanhadorResposta {
  numero: string;
  email: string;
  tipo_rifa: string;
  local_sorteio: string;
}

interface GanhadoresResponse {
  rifa_id: string;
  resultado: {
    valor: string | null;
    local_sorteio: string | null;
    data_resultado: string | null;
    apurado: boolean;
  } | null;
  ganhadores: GanhadorResposta[];
}

const AdminApuracao: React.FC = () => {
  const { token, user } = useAuth();
  const [rifasEncerradas, setRifasEncerradas] = useState<Rifa[]>([]);
  const [rifaSelecionada, setRifaSelecionada] = useState<string>("");
  const [resumo, setResumo] = useState<RifaResumo | null>(null);
  const [ganhadoresResponse, setGanhadoresResponse] =
    useState<GanhadoresResponse | null>(null);
  const [resultadoForm, setResultadoForm] = useState({
    resultado: "",
    data_resultado: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const formatNumero = (num: string, tipo?: string) => {
      if (!tipo) return num;
      const t = tipo.toLowerCase();
      if (t === 'dezena' && num === '100') return '00';
      if (t === 'centena' && num === '1000') return '000';
      if (t === 'milhar' && num === '10000') return '0000';
      return num;
  };

  const getMaxLength = (tipo: RifaTipo) => {
    switch (tipo) {
      case RifaTipo.MILHAR:
        return 4;
      case RifaTipo.CENTENA:
        return 3;
      case RifaTipo.DEZENA:
        return 2;
      case RifaTipo.GRUPO:
        return 2;
      default:
        return 100;
    }
  };

  useEffect(() => {
    if (!token || user?.role !== "admin") {
      return;
    }
    carregarRifasEncerradas();
  }, [token, user]);

  useEffect(() => {
    if (!rifaSelecionada) {
      setResumo(null);
      setGanhadoresResponse(null);
      return;
    }

    // Set default date to now (local time)
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    setResultadoForm((prev) => ({
      ...prev,
      data_resultado: now.toISOString().slice(0, 16),
      resultado: "", // Clear previous result to avoid confusion
    }));

    carregarResumo();
    carregarGanhadores();
  }, [rifaSelecionada]);

  const headers = token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : undefined;

  const carregarRifasEncerradas = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || "/api/v1";
      const res = await axios.get<Rifa[]>(
        `${apiUrl}/rifas/`,
        { headers }
      );
      const filtradas = res.data.filter(
        (r) =>
          r.status === RifaStatus.ATIVA ||
          r.status === RifaStatus.ENCERRADA ||
          r.status === RifaStatus.APURADA
      );
      setRifasEncerradas(filtradas);
      if (!rifaSelecionada && filtradas.length > 0) {
        setRifaSelecionada(filtradas[0].id);
      }
    } catch (e) {
      setError(mapApiError(e));
    } finally {
      setLoading(false);
    }
  };

  const carregarResumo = async () => {
    if (!rifaSelecionada) return;
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
      const res = await axios.get<RifaResumo>(
        `${apiUrl}/admin/rifas/${rifaSelecionada}/resumo`,
        { headers }
      );
      setResumo(res.data);
    } catch (e) {
      setError(mapApiError(e));
    }
  };

  const carregarGanhadores = async () => {
    if (!rifaSelecionada) return;
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
      const res = await axios.get<GanhadoresResponse>(
        `${apiUrl}/admin/rifas/${rifaSelecionada}/ganhadores`,
        { headers }
      );
      setGanhadoresResponse(res.data);
    } catch (e) {
      setError(mapApiError(e));
    }
  };

  const handleSubmitResultado = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rifaSelecionada) return;
    
    const selectedRifa = rifasEncerradas.find((r) => r.id === rifaSelecionada);
    if (!selectedRifa) {
      setError("Rifa não encontrada");
      return;
    }

    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
      await axios.post(
        `${apiUrl}/admin/rifas/${rifaSelecionada}/resultado`,
        {
          resultado: resultadoForm.resultado,
          local_sorteio: selectedRifa.local_sorteio,
          data_resultado: new Date(resultadoForm.data_resultado).toISOString(),
        },
        { headers }
      );
      setMessage("Resultado lançado com sucesso");
      setResultadoForm({
        resultado: "",
        data_resultado: "",
      });
      await carregarResumo();
    } catch (err: any) {
      setError(mapApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleApurar = async () => {
    if (!rifaSelecionada) return;
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      await axios.post(
        `http://localhost:8000/api/v1/admin/rifas/${rifaSelecionada}/apurar`,
        {},
        { headers }
      );
      setMessage("Rifa apurada com sucesso");
      await carregarResumo();
      await carregarGanhadores();
      await carregarRifasEncerradas();
    } catch (err: any) {
      setError(mapApiError(err));
    } finally {
      setLoading(false);
    }
  };

  if (user?.role !== "admin") {
    return (
      <div className="p-5 text-gray-900 dark:text-white">
        <h2 className="text-xl font-bold">Restrito ao administrador</h2>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Apuração de Rifas
        </h1>
      </div>

      {error && (
        <div className="mb-4 p-4 rounded-md bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30">
          {error}
        </div>
      )}
      {message && (
        <div className="mb-4 p-4 rounded-md bg-green-50 text-green-700 border border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30">
          {message}
        </div>
      )}

      <div className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6 mb-6 border border-gray-200 dark:border-slate-700">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Selecione a Rifa Encerrada</label>
          <select
            value={rifaSelecionada}
            onChange={(e) => setRifaSelecionada(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
          >
            <option value="">Selecione uma rifa</option>
            {rifasEncerradas.map((r) => (
              <option key={r.id} value={r.id}>
                {r.titulo} ({r.status})
              </option>
            ))}
          </select>
        </div>

        {resumo && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-gray-50 dark:bg-slate-700/50 rounded-lg border border-gray-100 dark:border-slate-600">
              <span className="block text-sm text-gray-500 dark:text-gray-400">Total Arrecadado</span>
              <span className="text-xl font-bold text-green-600 dark:text-green-400">R$ {resumo.total_arrecadado.toFixed(2)}</span>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-slate-700/50 rounded-lg border border-gray-100 dark:border-slate-600">
              <span className="block text-sm text-gray-500 dark:text-gray-400">Números Pagos</span>
              <span className="text-xl font-bold text-blue-600 dark:text-blue-400">{resumo.total_numeros_pagos}</span>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-slate-700/50 rounded-lg border border-gray-100 dark:border-slate-600">
              <span className="block text-sm text-gray-500 dark:text-gray-400">Status Apuração</span>
              <span className={`text-xl font-bold ${resumo.resultado_lancado ? 'text-green-600 dark:text-green-400' : 'text-orange-500 dark:text-orange-400'}`}>
                {resumo.resultado_lancado ? 'Resultado Lançado' : 'Aguardando Resultado'}
              </span>
            </div>
          </div>
        )}

        {rifaSelecionada && (
          <form onSubmit={handleSubmitResultado} className="space-y-4 border-t border-gray-200 dark:border-slate-700 pt-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Lançar Resultado Oficial</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Número Sorteado</label>
                <input
                  type="text"
                  value={resultadoForm.resultado}
                  onChange={(e) => {
                    const selectedRifa = rifasEncerradas.find((r) => r.id === rifaSelecionada);
                    const maxLength = selectedRifa ? getMaxLength(selectedRifa.tipo_rifa) : 100;
                    const val = e.target.value.replace(/\D/g, "").slice(0, maxLength);
                    setResultadoForm({ ...resultadoForm, resultado: val });
                  }}
                  required
                  placeholder="Ex: 1234"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Data Resultado</label>
                <input
                  type="datetime-local"
                  value={resultadoForm.data_resultado}
                  onChange={(e) => setResultadoForm({...resultadoForm, data_resultado: e.target.value})}
                  required
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Processando...' : 'Salvar Resultado'}
            </button>
          </form>
        )}
      </div>

      {resumo?.resultado_lancado && (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-slate-700">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Processar Apuração</h3>
            <button
              onClick={handleApurar}
              disabled={loading}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md shadow-sm text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Apurando...' : 'Apurar Vencedores Agora'}
            </button>
          </div>

          {ganhadoresResponse && ganhadoresResponse.ganhadores.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
                <thead className="bg-gray-50 dark:bg-slate-700">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Número</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Ganhador (Email)</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Tipo</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-slate-800 divide-y divide-gray-200 dark:divide-slate-700">
                  {ganhadoresResponse.ganhadores.map((g, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-slate-700/50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 dark:text-white">{formatNumero(g.numero, g.tipo_rifa)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{g.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{g.tipo_rifa}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              Nenhum ganhador apurado ainda ou nenhum acertador.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminApuracao;