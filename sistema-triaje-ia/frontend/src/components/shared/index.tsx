export function LoadingSpinner({ message = 'Cargando...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className="w-8 h-8 border-4 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
      <p className="text-sm text-slate-500">{message}</p>
    </div>
  )
}

export function ErrorAlert({ error, onRetry }: { error: string; onRetry?: () => void }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <p className="text-red-700 text-sm">{error}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-2 text-sm text-red-600 underline">
          Reintentar
        </button>
      )}
    </div>
  )
}

export function EmptyState({ message = 'Sin datos disponibles' }: { message?: string }) {
  return (
    <div className="text-center py-12">
      <p className="text-slate-400">{message}</p>
    </div>
  )
}
