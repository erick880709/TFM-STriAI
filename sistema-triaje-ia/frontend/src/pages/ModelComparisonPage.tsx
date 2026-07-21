import { useQuery } from '@tanstack/react-query'
import { modelsApi, type DiskModel } from '../api/models'
import { LoadingSpinner, ErrorAlert, EmptyState } from '../components/shared'

export default function ModelComparisonPage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['models-disk'],
    queryFn: () => modelsApi.scanDisk().then(r => r.data.data),
  })

  if (isLoading) return <LoadingSpinner message="Cargando modelos..." />
  if (isError) return <ErrorAlert error={`Error al cargar modelos: ${(error as Error)?.message || 'Error desconocido'}`} onRetry={() => refetch()} />
  if (!data || data.length === 0) return <EmptyState message="No se encontraron modelos serializados en disco." />

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-1">🔬 Comparar Modelos</h1>
      <p className="text-sm text-slate-500 mb-6">Comparativa de métricas entre versiones de modelos IA</p>

      <div className="overflow-x-auto">
        <table className="w-full bg-white border border-slate-200 rounded-lg">
          <caption className="sr-only">Tabla comparativa de métricas de modelos IA</caption>
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase">
              <th scope="col" className="px-4 py-3">Nombre</th>
              <th scope="col" className="px-4 py-3">Versión</th>
              <th scope="col" className="px-4 py-3">F1 Macro</th>
              <th scope="col" className="px-4 py-3">AUC-ROC</th>
              <th scope="col" className="px-4 py-3">Features</th>
              <th scope="col" className="px-4 py-3">Tamaño</th>
              <th scope="col" className="px-4 py-3">SHAP</th>
            </tr>
          </thead>
          <tbody>
            {(data || []).map((m: DiskModel) => (
              <tr key={m.version} className="border-b border-slate-100 hover:bg-slate-50 text-sm">
                <td className="px-4 py-3 font-medium text-slate-800">{m.nombre}</td>
                <td className="px-4 py-3 text-slate-500 font-mono text-xs">{m.version}</td>
                <td className="px-4 py-3">{m.f1_macro?.toFixed(3) || 'N/D'}</td>
                <td className="px-4 py-3">{m.auc_roc?.toFixed(3) || 'N/D'}</td>
                <td className="px-4 py-3">{m.n_features || '?'}</td>
                <td className="px-4 py-3">{m.tamano_mb ? `${m.tamano_mb} MB` : '?'}</td>
                <td className="px-4 py-3">{m.shap_disponible ? 'Disponible' : 'No disponible'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
