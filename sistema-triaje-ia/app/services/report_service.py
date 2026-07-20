"""
Servicio de Reportes — HU-E5-02.
Genera el registro de triaje descargable (PDF/HTML) con datos anonimizados,
cumpliendo con los requisitos de la Resolución 5596/2015.

Referencia: Mockup P12, RNAU-001 a 006.
"""
import io
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class ReportService:
    """Genera reportes descargables del sistema de triaje."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.audit_svc = AuditService(db_path)

    # ------------------------------------------------------------------
    # HU-E5-02: Registro de Triaje descargable
    # ------------------------------------------------------------------
    def generate_triage_html(self, id_triaje: str) -> str:
        """
        Genera un reporte HTML del evento de triaje completo,
        listo para visualización o impresión a PDF.
        """
        data = self.audit_svc.generate_triage_report(id_triaje)

        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Registro de Triaje — {id_triaje}</title>
<style>
  @page {{ margin: 15mm; size: A4; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; color: #1E293B; margin: 0; padding: 20px; }}
  .header {{ text-align: center; border-bottom: 3px solid #0891B2; padding-bottom: 10px; margin-bottom: 20px; }}
  .header h1 {{ color: #164E63; font-size: 20px; margin: 0; }}
  .header .subtitle {{ color: #64748B; font-size: 11px; margin-top: 4px; }}
  .meta {{ display: flex; justify-content: space-between; background: #F1F5F9; padding: 10px 15px; border-radius: 6px; margin-bottom: 15px; }}
  .meta div {{ flex: 1; }}
  .meta .label {{ font-size: 9px; color: #64748B; text-transform: uppercase; }}
  .meta .value {{ font-size: 13px; font-weight: 600; color: #0F172A; }}
  .section {{ margin-bottom: 18px; page-break-inside: avoid; }}
  .section h2 {{ font-size: 14px; color: #0891B2; border-bottom: 1px solid #E2E8F0; padding-bottom: 4px; margin-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 10px; }}
  td {{ padding: 4px 8px; border-bottom: 1px solid #F1F5F9; }}
  td.label {{ color: #64748B; width: 40%; font-weight: 500; }}
  td.value {{ color: #0F172A; font-weight: 600; }}
  .classification {{ display: flex; gap: 20px; margin: 15px 0; }}
  .class-box {{ flex: 1; padding: 15px; border-radius: 8px; text-align: center; }}
  .class-box.ia {{ background: #FFF7ED; border: 2px solid #EA580C; }}
  .class-box.prof {{ background: #F0FDF4; border: 2px solid #059669; }}
  .class-box .box-label {{ font-size: 9px; text-transform: uppercase; color: #64748B; }}
  .class-box .box-level {{ font-size: 36px; font-weight: 700; margin: 5px 0; }}
  .class-box.ia .box-level {{ color: #EA580C; }}
  .class-box.prof .box-level {{ color: #059669; }}
  .concordance {{ text-align: center; padding: 8px; border-radius: 6px; margin: 10px 0; font-weight: 600; }}
  .concordance.yes {{ background: #F0FDF4; color: #059669; }}
  .concordance.no {{ background: #FEF2F2; color: #DC2626; }}
  .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #E2E8F0; font-size: 9px; color: #94A3B8; text-align: center; }}
  .footer .disclaimer {{ font-style: italic; }}
  @media print {{ body {{ padding: 0; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>📋 Registro de Evento de Triaje</h1>
  <div class="subtitle">Sistema de Triaje Multimodal IA — TFM UNIR · Resolución 5596/2015</div>
</div>

<div class="meta">
  <div>
    <div class="label">ID del Evento</div>
    <div class="value">{data.get('id_triaje', '')}</div>
  </div>
  <div>
    <div class="label">Fecha de Ingreso</div>
    <div class="value">{data.get('fecha_ingreso', '')[:19]}</div>
  </div>
  <div>
    <div class="label">Estado</div>
    <div class="value">{data.get('estado', '')}</div>
  </div>
  <div>
    <div class="label">Generado</div>
    <div class="value">{now}</div>
  </div>
</div>

<!-- CLASIFICACIÓN -->
<div class="section">
  <h2>🎯 Clasificación del Triaje</h2>
  <div class="classification">
    <div class="class-box ia">
      <div class="box-label">🤖 Sugerencia IA</div>
      <div class="box-level">{data.get('nivel_ia', '—')}</div>
      <div style="font-size:10px; color:#64748B;">{data.get('nivel_ia_label', '')}</div>
      <div style="font-size:9px; margin-top:5px;">Confianza: {data.get('confianza_ia', '—')}</div>
    </div>
    <div class="class-box prof">
      <div class="box-label">👨‍⚕️ Profesional</div>
      <div class="box-level">{data.get('nivel_profesional', '—')}</div>
      <div style="font-size:10px; color:#64748B;">{data.get('nivel_profesional_label', '')}</div>
    </div>
  </div>
  <div class="concordance {'yes' if data.get('concordancia') == 'Sí' else 'no'}">
    {'✅ CONCORDANCIA: Ambos coinciden' if data.get('concordancia') == 'Sí' else '⚠️ DISCREPANCIA: Los niveles difieren'}
  </div>
  {f'<p style="font-size:10px;"><strong>Motivo de discrepancia:</strong> {data.get("motivo_discrepancia", "")}</p>' if data.get("motivo_discrepancia") else ''}
  <p style="font-size:9px; color:#64748B;">Modelo: {data.get('version_modelo', 'N/A')}</p>
</div>

<!-- DATOS DEL PACIENTE (anonimizado) -->
<div class="section">
  <h2>👤 Datos del Paciente (Anonimizado — Ley 1581/2012)</h2>
  <table>
    <tr><td class="label">Edad</td><td class="value">{data.get('edad_paciente', '—')} años</td></tr>
    <tr><td class="label">Sexo</td><td class="value">{data.get('sexo', '—')}</td></tr>
    <tr><td class="label">Vía de Llegada</td><td class="value">{data.get('via_llegada', '—')}</td></tr>
    <tr><td class="label">Episodios Previos</td><td class="value">{data.get('episodios_previos', '0')}</td></tr>
  </table>
</div>

<!-- SIGNOS VITALES -->
<div class="section">
  <h2>💓 Signos Vitales</h2>
  <table>
    <tr><td class="label">Temperatura</td><td class="value">{data.get('temperatura', '—')} °C</td></tr>
    <tr><td class="label">Frecuencia Cardíaca</td><td class="value">{data.get('frecuencia_cardiaca', '—')} lpm</td></tr>
    <tr><td class="label">Frecuencia Respiratoria</td><td class="value">{data.get('frecuencia_respiratoria', '—')} rpm</td></tr>
    <tr><td class="label">Saturación O₂</td><td class="value">{data.get('saturacion_o2', '—')}%</td></tr>
    <tr><td class="label">Presión Arterial</td><td class="value">{data.get('presion_sistolica', '—')}/{data.get('presion_diastolica', '—')} mmHg</td></tr>
    <tr><td class="label">IMC</td><td class="value">{data.get('imc', '—')} kg/m² (Peso: {data.get('peso', '—')} kg, Talla: {data.get('talla', '—')} cm)</td></tr>
  </table>
</div>

<!-- EVALUACIÓN CLÍNICA -->
<div class="section">
  <h2>🩺 Evaluación Clínica</h2>
  <table>
    <tr><td class="label">Motivo de Consulta</td><td class="value">{data.get('motivo_categoria', '—')}</td></tr>
    <tr><td class="label">Texto Libre</td><td class="value">{data.get('motivo_texto_libre', '—') or 'No registrado'}</td></tr>
    <tr><td class="label">Escala de Dolor</td><td class="value">{data.get('escala_dolor', '—')}/10</td></tr>
    <tr><td class="label">Glasgow</td><td class="value">{data.get('glasgow', '—')}/15</td></tr>
    <tr><td class="label">Nivel de Conciencia</td><td class="value">{data.get('nivel_conciencia', '—')}</td></tr>
    <tr><td class="label">Antecedentes</td><td class="value">{', '.join(data.get('antecedentes', [])) if data.get('antecedentes') else 'Ninguno'}</td></tr>
    <tr><td class="label">Alergias</td><td class="value">{data.get('alergias', '—') or 'No registradas'}</td></tr>
    <tr><td class="label">Observaciones</td><td class="value">{data.get('observaciones', '—') or 'Ninguna'}</td></tr>
  </table>
</div>

<!-- PROBABILIDADES IA -->
<div class="section">
  <h2>📊 Probabilidades del Modelo IA</h2>
  <table>
    {_render_probability_rows(data.get('probabilidades_ia', {}))}
  </table>
</div>

<!-- AUDITORÍA -->
<div class="section">
  <h2>🔍 Trazabilidad</h2>
  <table>
    <tr><td class="label">Total de acciones registradas</td><td class="value">{data.get('total_acciones_auditadas', 0)}</td></tr>
    <tr><td class="label">Profesional Responsable</td><td class="value">{data.get('profesional_responsable', 'N/A')}</td></tr>
    <tr><td class="label">Fecha de Cierre</td><td class="value">{data.get('fecha_cierre', '—') or 'No cerrado'}</td></tr>
  </table>
</div>

<div class="footer">
  <p>{data.get('sistema', '')}</p>
  <p class="disclaimer">
    ⚠️ Este documento es generado automáticamente como apoyo al profesional sanitario.
    La decisión final de clasificación corresponde al profesional de la salud.
    Los datos del paciente han sido anonimizados según la Ley 1581 de 2012.
  </p>
  <p>Generado el {now} · Versión 1.0</p>
</div>

</body>
</html>"""
        return html

    def get_triage_html_bytes(self, id_triaje: str) -> bytes:
        """Retorna el HTML del reporte como bytes para descarga."""
        html = self.generate_triage_html(id_triaje)
        return html.encode("utf-8")


def _render_probability_rows(probs: dict) -> str:
    """Renderiza filas de probabilidades con barras de color."""
    if not probs:
        return '<tr><td class="label" colspan="2">No disponible</td></tr>'

    colors = {
        "I": "#DC2626", "II": "#EA580C", "III": "#F59E0B",
        "IV": "#059669", "V": "#0891B2",
    }
    icons = {"I": "🔴", "II": "🟠", "III": "🟡", "IV": "🟢", "V": "🔵"}

    rows = ""
    for nivel in ["I", "II", "III", "IV", "V"]:
        prob = probs.get(nivel, 0)
        color = colors.get(nivel, "#64748B")
        icon = icons.get(nivel, "")
        bar_width = int(prob * 100)
        rows += f"""
        <tr>
          <td class="label">{icon} Nivel {nivel}</td>
          <td class="value" style="color:{color};">
            {prob:.1%}
            <div style="background:#F1F5F9; border-radius:4px; height:8px; margin-top:2px;">
              <div style="background:{color}; width:{bar_width}%; height:8px; border-radius:4px;"></div>
            </div>
          </td>
        </tr>"""
    return rows
