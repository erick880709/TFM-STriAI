export const TIPOS_DOCUMENTO = ['CC', 'CE', 'TI', 'PA', 'RC'] as const
export const GRUPOS_SANGUINEOS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'] as const
export const EPS_COLOMBIA = [
  'Aliansalud', 'Anas Wayuu', 'Asmet Salud', 'Cajacopi', 'Capital Salud',
  'Comparta', 'Comfenalco Valle', 'Coosalud', 'Emssanar', 'Famisanar',
  'Mallamas', 'Mutual Ser', 'Nueva EPS', 'Salud Total', 'Sanitas',
  'Savia Salud', 'Solsalud', 'SOS', 'Sumimedical', 'Supersalud', 'SurA',
] as const
export const VIAS_LLEGADA = ['Caminando', 'Silla de ruedas', 'Camilla', 'Ambulancia'] as const
export const DEPARTAMENTOS_COLOMBIA = [
  'Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá',
  'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó', 'Córdoba',
  'Cundinamarca', 'Guainía', 'Guaviare', 'Huila', 'La Guajira',
  'Magdalena', 'Meta', 'Nariño', 'Norte de Santander', 'Putumayo',
  'Quindío', 'Risaralda', 'San Andrés y Providencia', 'Santander',
  'Sucre', 'Tolima', 'Valle del Cauca', 'Vaupés', 'Vichada',
] as const
export const NIVELES_TRIAGE = ['I', 'II', 'III', 'IV', 'V'] as const
export const NIVELES_COLORS: Record<string, string> = {
  I: '#DC2626', II: '#EA580C', III: '#F59E0B', IV: '#059669', V: '#0891B2',
}
export const ESTADOS_TRIAGE = [
  'Registrado', 'EnEvaluacion', 'PendienteIA', 'Clasificado', 'Validado', 'Cerrado', 'Cancelado',
] as const
export const NIVELES_CONCIENCIA = ['Alerta', 'Confuso', 'Somnoliento', 'Estuporoso', 'Coma'] as const
export const COMORBILIDADES = [
  'Hipertension', 'Diabetes', 'EPOC', 'Cardiopatia', 'IRC', 'Cancer', 'Inmunosupresion', 'Obesidad',
] as const
