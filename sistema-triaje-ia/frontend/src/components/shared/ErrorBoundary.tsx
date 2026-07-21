import { Component, type ReactNode } from 'react'

interface Props { children: ReactNode; fallback?: ReactNode }
interface State { hasError: boolean; error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 p-8">
          <div className="text-4xl">⚠️</div>
          <h2 className="text-xl font-semibold text-[#164E63]" style={{fontFamily:'Lexend,system-ui,sans-serif'}}>Algo salió mal</h2>
          <p className="text-sm text-[#64748B] text-center max-w-md">
            Ocurrió un error inesperado al cargar esta sección.
            Intenta recargar la página.
          </p>
          {this.state.error && (
            <pre className="text-xs text-red-600 bg-red-50 p-3 rounded-lg max-w-lg overflow-auto">
              {this.state.error.message}
            </pre>
          )}
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-[#0891B2] text-white rounded-lg text-sm hover:bg-[#0E7490] transition-colors"
          >
            Recargar página
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
