import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { MinhaRifa, NumeroStatus, PremioStatus, RifaStatus } from "../types";
import { mapApiError } from "../utils/mapApiError";

const MinhasCompras: React.FC = () => {
  const { token } = useAuth();
  const [rifas, setRifas] = useState<MinhaRifa[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      setError("Você precisa estar autenticado para ver suas compras.");
      return;
    }
    fetchData();
  }, [token]);

  const fetchData = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '/api/v1';
      const response = await axios.get<MinhaRifa[]>(
        `${apiUrl}/rifas/user/minhas-rifas`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setRifas(response.data);
    } catch (err) {
      setError(mapApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const formatStatusPremio = (status: PremioStatus) => {
    if (status === "WINNER") return "Ganhou";
    if (status === "LOSER") return "Não ganhou";
    return "Aguardando apuração";
  };

  const getBadgeClasses = (status: PremioStatus) => {
    if (status === "WINNER")
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300";
    if (status === "LOSER")
      return "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300";
    return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300";
  };

  if (loading)
    return (
      <div className="p-5 text-gray-900 dark:text-gray-100">
        Carregando suas compras...
      </div>
    );

  if (error)
    return (
      <div className="p-5 text-red-600 dark:text-red-400">
        {error}
      </div>
    );

  if (rifas.length === 0)
    return (
      <div className="p-5 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Minhas Compras
        </h1>
        <div className="p-8 bg-white dark:bg-gray-800 rounded-lg shadow text-center text-gray-600 dark:text-gray-300">
          Você ainda não possui números comprados.
        </div>
      </div>
    );

  return (
    <div className="p-5 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Minhas Compras
      </h1>

      <div className="space-y-6">
        {rifas.map((rifa) => {
          const hasWinner = rifa.numeros_comprados.some(
            (n) => n.premio_status === "WINNER"
          );

          return (
            <div
              key={rifa.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700"
            >
              <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {rifa.titulo}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Sorteio em {new Date(rifa.data_sorteio).toLocaleString()}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold ${
                      rifa.status === RifaStatus.APURADA
                        ? "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300"
                        : rifa.status === RifaStatus.ENCERRADA
                        ? "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300"
                        : "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                    }`}
                  >
                    {rifa.status}
                  </span>
                  {rifa.resultado && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Resultado: {rifa.resultado}
                    </span>
                  )}
                  {hasWinner && (
                    <span className="text-xs font-semibold text-green-600 dark:text-green-400">
                      Você possui números premiados nesta rifa
                    </span>
                  )}
                </div>
              </div>

              <div className="px-5 py-4">
                <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-3">
                  Números comprados
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-900/40">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Número
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Resultado
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Data compra
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {rifa.numeros_comprados.map((n, idx) => (
                        <tr
                          key={`${n.numero}-${idx}`}
                          className="hover:bg-gray-50 dark:hover:bg-gray-900/40"
                        >
                          <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {n.numero}
                          </td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                            {n.status === NumeroStatus.PAGO ? "Pago" : n.status}
                          </td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm">
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-semibold ${getBadgeClasses(
                                n.premio_status
                              )}`}
                            >
                              {formatStatusPremio(n.premio_status)}
                            </span>
                          </td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {n.data_compra
                              ? new Date(n.data_compra).toLocaleString()
                              : "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MinhasCompras;

