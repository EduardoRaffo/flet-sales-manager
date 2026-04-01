"""
Generación de informe HTML para pipeline de leads.

Consume datos ya cargados en LeadsView:
- leads (lista filtrada o completa)
- funnel_stats (de get_funnel_stats)
- sources_data (de group_leads_by_source)
- marketing_summary (de get_marketing_efficiency_summary)
- marketing_metrics (de get_marketing_metrics)

NO realiza queries adicionales.
"""
import html
import os
from datetime import datetime
from .html_template import get_html_base
from .charts_generator import generate_pie_chart, generate_horizontal_bar_chart
from utils.formatting import format_eur


# Source labels coherentes con tabla_leads.py
_SOURCE_LABELS = {
    "meta_ads":      "Meta Ads",
    "google_ads":    "Google Ads",
    "linkedin_ads":  "LinkedIn Ads",
    "tiktok_ads":    "TikTok Ads",
    "manual_import": "Manual",
}

_STATUS_LABELS = {
    "new":       "Lead",
    "contacted": "Contactado",
    "meeting":   "Reunión",
    "converted": "Cliente",
    "lost":      "Perdido",
}

_STATUS_BADGE_CLASS = {
    "new":       "badge-new",
    "contacted": "badge-contacted",
    "meeting":   "badge-meeting",
    "converted": "badge-converted",
    "lost":      "badge-lost",
}

_FUNNEL_COLORS = {
    "leads":     "#1565C0",
    "meetings":  "#e65100",
    "converted": "#2e7d32",
}


def generate_leads_html_report(
    leads: list,
    funnel_stats: dict,
    sources_data: dict,
    filters_desc: str = "Todos los leads",
    filename: str = None,
    marketing_summary: dict = None,
    marketing_metrics: list = None,
):
    """
    Genera un informe HTML del pipeline de leads.

    Args:
        leads: Lista de leads enriched (filtrados o totales)
        funnel_stats: dict de get_funnel_stats()
        sources_data: dict de group_leads_by_source()
        filters_desc: Descripción textual de los filtros activos
        filename: Ruta del archivo (si es None, genera uno automático)
        marketing_summary: dict de get_marketing_efficiency_summary() (opcional)
        marketing_metrics: list de get_marketing_metrics() (opcional)

    Returns:
        tuple (success: bool, message: str, filepath: str)
    """
    try:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Informe_Leads_{timestamp}.html"

        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        # ── Funnel section ───────────────────────────────────────
        total = funnel_stats.get("total", 0)
        meetings = funnel_stats.get("meetings", 0)
        converted = funnel_stats.get("converted", 0)

        funnel_html = _render_funnel(total, meetings, converted)

        # ── KPI metrics ──────────────────────────────────────────
        lead_to_meeting_pct = funnel_stats.get("lead_to_meeting_pct", 0)
        meeting_to_client_pct = funnel_stats.get("meeting_to_client_pct", 0)
        avg_time = funnel_stats.get("avg_time_to_meeting", 0)

        kpi_html = f'''
        <div class="metrics">
            <div class="metric-card">
                <label>Total Leads</label>
                <div class="value">{total}</div>
            </div>
            <div class="metric-card accent-orange">
                <label>Reuniones</label>
                <div class="value">{meetings}</div>
            </div>
            <div class="metric-card accent-green">
                <label>Clientes Convertidos</label>
                <div class="value">{converted}</div>
            </div>
            <div class="metric-card accent-purple">
                <label>Lead &rarr; Reunión</label>
                <div class="value">{lead_to_meeting_pct:.1f}%</div>
            </div>
            <div class="metric-card accent-teal">
                <label>Reunión &rarr; Cliente</label>
                <div class="value">{meeting_to_client_pct:.1f}%</div>
            </div>
            <div class="metric-card accent-orange">
                <label>Tiempo medio a reunión</label>
                <div class="value">{avg_time:.0f} días</div>
            </div>
        </div>
        '''

        # ── Source distribution chart ────────────────────────────
        source_chart_html = ""
        if sources_data:
            src_labels = [_SOURCE_LABELS.get(s, s) for s in sources_data]
            src_values = [float(d["total"]) for d in sources_data.values()]

            try:
                pie_b64 = generate_pie_chart(src_labels, src_values)
                source_chart_html = f'''
                <div class="chart-container">
                    <h3>Distribución por Fuente</h3>
                    <img src="data:image/png;base64,{pie_b64}" style="width:100%;">
                </div>
                '''
            except Exception:
                pass

        # ── Source conversion table ───────────────────────────────
        source_table_html = ""
        if sources_data:
            rows_html = ""
            for src, data in sorted(sources_data.items(), key=lambda x: x[1]["total"], reverse=True):
                s_total = data["total"]
                s_meetings = data["meetings"]
                s_clients = data["clients"]
                s_conv = (s_clients / s_total * 100) if s_total else 0
                s_m2c = data.get("meeting_to_client_pct", 0)
                s_avg = data.get("avg_time_to_meeting", 0)
                rows_html += f'''<tr>
                    <td><strong>{_SOURCE_LABELS.get(src, src)}</strong></td>
                    <td>{s_total}</td>
                    <td>{s_meetings}</td>
                    <td>{s_clients}</td>
                    <td>{s_conv:.1f}%</td>
                    <td>{s_m2c:.1f}%</td>
                    <td>{s_avg:.0f}d</td>
                </tr>
'''
            source_table_html = f'''
            <h2>Rendimiento por Fuente</h2>
            {source_chart_html}
            <table>
                <thead>
                    <tr>
                        <th>Fuente</th>
                        <th>Leads</th>
                        <th>Reuniones</th>
                        <th>Clientes</th>
                        <th>Conv. Total</th>
                        <th>Reunión &rarr; Cliente</th>
                        <th>Tiempo medio</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            '''

        # ── Leads table ──────────────────────────────────────────
        leads_table_html = ""
        if leads:
            rows_html = ""
            for ld in leads[:50]:  # Limitar a 50 leads en el export
                created = (ld.get("created_at") or "")[:10]
                source = html.escape(_SOURCE_LABELS.get(ld.get("source", ""), ld.get("source", "—")))
                status_raw = (ld.get("status") or "").lower().strip()
                status_label = html.escape(_STATUS_LABELS.get(status_raw, status_raw))
                badge_class = _STATUS_BADGE_CLASS.get(status_raw, "badge-new")
                meeting = (ld.get("meeting_date") or "")[:10] if ld.get("meeting_date") else "—"
                client_name = html.escape(ld.get("client_name") or "—")

                rows_html += f'''<tr>
                    <td>{created}</td>
                    <td>{source}</td>
                    <td><span class="badge {badge_class}">{status_label}</span></td>
                    <td>{meeting}</td>
                    <td>{client_name}</td>
                </tr>
'''

            count_note = f" (mostrando primeros 50 de {len(leads)})" if len(leads) > 50 else ""
            leads_table_html = f'''
            <h2>Listado de Leads{count_note}</h2>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Fuente</th>
                        <th>Estado</th>
                        <th>Reunión</th>
                        <th>Cliente</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            '''

        # ── Marketing Performance section ─────────────────────
        marketing_html = ""
        if marketing_summary:
            overall_roi = marketing_summary.get("overall_roi", 0.0)
            roi_color = "#2e7d32" if overall_roi >= 0 else "#c62828"
            roi_str = f"{overall_roi * 100:.1f}%"

            marketing_html += f'''
            <h2>Marketing Performance <span style="font-size:12px;color:#666;font-weight:400;">· reactivo a los filtros activos</span></h2>
            <div class="metrics">
                <div class="metric-card accent-orange">
                    <label>Inversi&oacute;n Total</label>
                    <div class="value">{format_eur(marketing_summary.get("total_spend", 0))}</div>
                </div>
                <div class="metric-card accent-green">
                    <label>Revenue Atribuido</label>
                    <div class="value">{format_eur(marketing_summary.get("total_revenue", 0))}</div>
                </div>
                <div class="metric-card">
                    <label>CPL (Coste por Lead)</label>
                    <div class="value">{format_eur(marketing_summary.get("avg_cpl", 0))}</div>
                </div>
                <div class="metric-card accent-purple">
                    <label>CAC (Coste por Cliente)</label>
                    <div class="value">{format_eur(marketing_summary.get("avg_cac", 0))}</div>
                </div>
                <div class="metric-card" style="color:{roi_color}">
                    <label>ROI Global</label>
                    <div class="value" style="color:{roi_color}">{roi_str}</div>
                </div>
            </div>
            '''

        if marketing_metrics:
            mkt_rows = ""
            for m in marketing_metrics:
                src_label = html.escape(_SOURCE_LABELS.get(m["source"], m["source"]))
                roi = m.get("roi", 0.0)
                roi_pct = roi * 100
                roi_color = "#2e7d32" if roi >= 0 else "#c62828"
                mkt_rows += f'''<tr>
                    <td><strong>{src_label}</strong></td>
                    <td>{m.get("leads", 0)}</td>
                    <td>{m.get("customers", 0)}</td>
                    <td>{format_eur(m.get("revenue", 0))}</td>
                    <td>{format_eur(m.get("spend", 0))}</td>
                    <td>{format_eur(m.get("cpl", 0))}</td>
                    <td>{format_eur(m.get("cac", 0))}</td>
                    <td style="color:{roi_color};font-weight:600">{roi_pct:.1f}%</td>
                </tr>
'''
            marketing_html += f'''
            <h3>Detalle por Fuente</h3>
            <table>
                <thead>
                    <tr>
                        <th>Fuente</th><th>Leads</th><th>Clientes</th>
                        <th>Revenue</th><th>Inversi&oacute;n</th>
                        <th>CPL</th><th>CAC</th><th>ROI</th>
                    </tr>
                </thead>
                <tbody>{mkt_rows}</tbody>
            </table>
            '''

        # ── Filters description ──────────────────────────────────
        filters_html = f'''
        <div class="period-filters">
            <div class="period-section">
                <span class="period-icon">📋</span>
                <span class="period-text">{html.escape(filters_desc)}</span>
            </div>
        </div>
        '''

        # ── Assemble content ─────────────────────────────────────
        content_block = f'''
        <div class="header">
            <div class="brand">Sales CRM</div>
            <h1>Informe de Leads</h1>
            <p>Generado el {datetime.now().strftime("%d de %B de %Y a las %H:%M:%S")}</p>
        </div>
        <div class="content">
            {filters_html}
            <h2>Embudo de Conversión</h2>
            {funnel_html}
            <h2>Métricas del Pipeline</h2>
            {kpi_html}
            {source_table_html}
            {marketing_html}
            {leads_table_html}
        </div>
        <div class="footer">
            <p><strong>Sales CRM</strong></p>
            <p>Informe generado automáticamente por el sistema de gestión de leads.</p>
            <p>&copy; {datetime.now().year} Sales CRM Portfolio Project.</p>
        </div>
        '''

        html_content = get_html_base(content_block, title="Informe de Leads ")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return (True, f"Informe generado: {os.path.basename(filename)}", filename)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return (False, f"Error al generar informe de leads: {str(e)}", None)


def _render_funnel(total: int, meetings: int, converted: int) -> str:
    """Renderiza embudo visual en HTML usando las clases CSS del template."""
    stages = [
        ("Leads", total, _FUNNEL_COLORS["leads"], 100),
        ("Reuniones", meetings, _FUNNEL_COLORS["meetings"],
         (meetings / total * 100) if total else 0),
        ("Clientes", converted, _FUNNEL_COLORS["converted"],
         (converted / total * 100) if total else 0),
    ]

    html = ""
    for label, value, color, bar_pct in stages:
        pct_text = f"{bar_pct:.1f}%" if bar_pct < 100 else ""
        html += f'''
        <div class="funnel-stage">
            <div class="stage-bar" style="width: {max(bar_pct, 8)}%; background: {color};"></div>
            <span class="stage-label" style="color: {color};">{label}</span>
            <span class="stage-value" style="color: {color};">{value}</span>
            <span class="stage-pct">{pct_text}</span>
        </div>
        '''
    return html
