"""
Gerador de PDF do relatório mensal de operações OnePax.
Usa ReportLab (layout) + matplotlib (charts).
"""
import io
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image as RLImage, KeepTogether,
)
from reportlab.pdfgen import canvas as canvas_mod

from .relatorio_mensal import _br_num, _DIAS_SEMANA_PT


# ──────────────────────────── PALETA ────────────────────────────
BRAND_RED = colors.HexColor('#8B0000')
DARK = colors.HexColor('#1A1A1A')
GRAY_900 = colors.HexColor('#222222')
GRAY_700 = colors.HexColor('#444444')
GRAY_500 = colors.HexColor('#666666')
GRAY_300 = colors.HexColor('#C4C4C4')
GRAY_100 = colors.HexColor('#F5F5F5')
GREEN = colors.HexColor('#16A34A')
RED_ALERT = colors.HexColor('#B91C1C')
WHITE = colors.white

CHART_COLORS = ['#8B0000', '#1A1A1A', '#666666', '#999999', '#C4C4C4']

LOGO_PATH = Path(__file__).resolve().parent.parent.parent / 'frontend-onepax' / 'public' / 'Onepax_cabecalho.png'


# ──────────────────────────── ESTILOS ────────────────────────────
_styles = getSampleStyleSheet()


def _style(name, **kwargs):
    base = _styles['Normal'].clone(name)
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


S_H1 = _style('H1', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=DARK, spaceAfter=4)
S_H2 = _style('H2', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=BRAND_RED, spaceBefore=12, spaceAfter=6)
S_H3 = _style('H3', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=GRAY_500, spaceAfter=2)
S_BODY = _style('Body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=GRAY_900, alignment=TA_JUSTIFY)
S_INSIGHT = _style('Insight', fontName='Helvetica', fontSize=10, leading=15, textColor=GRAY_900, leftIndent=14, spaceAfter=8)
S_SMALL = _style('Small', fontName='Helvetica', fontSize=8, leading=11, textColor=GRAY_500)
S_KPI_LBL = _style('KpiLbl', fontName='Helvetica', fontSize=8, leading=10, textColor=GRAY_500, alignment=TA_CENTER)
S_KPI_VAL = _style('KpiVal', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=DARK, alignment=TA_CENTER)
S_KPI_SUB = _style('KpiSub', fontName='Helvetica', fontSize=8, leading=10, textColor=GRAY_700, alignment=TA_CENTER)
S_TITLE_WHITE = _style('TitleWhite', fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=WHITE)
S_SUBTITLE_WHITE = _style('SubWhite', fontName='Helvetica', fontSize=11, leading=14, textColor=colors.HexColor('#CCCCCC'))


# ──────────────────────────── CHARTS ────────────────────────────

def _chart_bar_diario(serie: list[dict], out_path: str, width_in: float = 7.4, height_in: float = 2.4):
    """Barras empilhadas: embarque (vermelho) + desembarque (cinza) por dia do mês."""
    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=120)
    fig.patch.set_facecolor('white')

    labels = [date.fromisoformat(d['data']).day for d in serie]
    emb = [d['embarque'] for d in serie]
    des = [d['desembarque'] for d in serie]

    ax.bar(labels, emb, color='#8B0000', label='Embarque', width=0.75)
    ax.bar(labels, des, bottom=emb, color='#444444', label='Desembarque', width=0.75)

    ax.set_xlabel('Dia do mês', fontsize=8, color='#666')
    ax.set_ylabel('Passageiros', fontsize=8, color='#666')
    ax.tick_params(axis='both', labelsize=7, colors='#666')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ccc')
    ax.spines['bottom'].set_color('#ccc')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
    ax.grid(axis='y', linestyle='--', linewidth=0.4, color='#eee')
    ax.set_axisbelow(True)
    ax.legend(fontsize=8, frameon=False, loc='upper right')

    fig.tight_layout(pad=0.4)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def _chart_dia_semana(media_por_dia: list[float], out_path: str, width_in: float = 4.0, height_in: float = 2.2):
    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=120)
    fig.patch.set_facecolor('white')
    cores = ['#8B0000' if v == max(media_por_dia) else '#999' for v in media_por_dia]
    ax.bar(_DIAS_SEMANA_PT, media_por_dia, color=cores, width=0.65)
    ax.set_ylabel('Pax/dia médio', fontsize=8, color='#666')
    ax.tick_params(axis='both', labelsize=7, colors='#666')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ccc')
    ax.spines['bottom'].set_color('#ccc')
    ax.grid(axis='y', linestyle='--', linewidth=0.4, color='#eee')
    ax.set_axisbelow(True)
    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def _chart_hora(hora_pax: list[int], out_path: str, width_in: float = 4.0, height_in: float = 2.2):
    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=120)
    fig.patch.set_facecolor('white')
    horas = list(range(24))
    max_h = max(hora_pax) if hora_pax else 0
    cores = ['#8B0000' if v == max_h and v > 0 else '#bbbbbb' for v in hora_pax]
    ax.bar(horas, hora_pax, color=cores, width=0.7)
    ax.set_xlabel('Hora do dia', fontsize=8, color='#666')
    ax.set_ylabel('Pax acumulados', fontsize=8, color='#666')
    ax.set_xticks(range(0, 24, 3))
    ax.tick_params(axis='both', labelsize=7, colors='#666')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ccc')
    ax.spines['bottom'].set_color('#ccc')
    ax.grid(axis='y', linestyle='--', linewidth=0.4, color='#eee')
    ax.set_axisbelow(True)
    fig.tight_layout(pad=0.3)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def _chart_donut_operadoras(operadoras: list[dict], out_path: str, width_in: float = 3.5, height_in: float = 3.0):
    """Donut chart das operadoras (top 5 + outros)."""
    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=120)
    fig.patch.set_facecolor('white')

    top5 = operadoras[:5]
    others_pax = sum(o['passageiros'] for o in operadoras[5:])
    labels = [o['nome'] for o in top5]
    sizes = [o['passageiros'] for o in top5]
    if others_pax > 0:
        labels.append('Outros')
        sizes.append(others_pax)

    cores = ['#8B0000', '#1A1A1A', '#666', '#999', '#bbb', '#ddd'][:len(labels)]
    wedges, _ = ax.pie(
        sizes, colors=cores, startangle=90,
        wedgeprops=dict(width=0.42, edgecolor='white', linewidth=1.5),
    )
    ax.legend(wedges, labels, fontsize=7, loc='center left',
              bbox_to_anchor=(1.0, 0.5), frameon=False)
    ax.set(aspect='equal')
    fig.tight_layout(pad=0.2)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


# ──────────────────────────── HEADERS / FOOTERS ────────────────────────────

class _PageDecorator:
    """Desenha capa (página 1) e cabeçalho/rodapé das demais."""

    def __init__(self, mes_extenso: str, periodo: dict):
        self.mes_extenso = mes_extenso
        self.periodo = periodo

    def __call__(self, c: canvas_mod.Canvas, doc):
        page_num = doc.page
        width, height = A4
        if page_num == 1:
            self._cover_header(c, width, height)
        else:
            self._page_header(c, width, height)
            self._page_footer(c, width, height, page_num)

    def _cover_header(self, c, width, height):
        # Banda preta no topo cobrindo header
        c.setFillColor(DARK)
        c.rect(0, height - 4.5 * cm, width, 4.5 * cm, stroke=0, fill=1)
        # Logo embutido na banda preta
        if LOGO_PATH.exists():
            try:
                logo = RLImage(str(LOGO_PATH), width=5.5 * cm, height=1.05 * cm)
                logo.drawOn(c, 2 * cm, height - 3.4 * cm)
            except Exception:
                pass
        # Linha vermelha embaixo da banda
        c.setFillColor(BRAND_RED)
        c.rect(0, height - 4.6 * cm, width, 0.1 * cm, stroke=0, fill=1)

    def _page_header(self, c, width, height):
        # Linha vermelha + logo pequeno + título
        c.setFillColor(DARK)
        c.rect(0, height - 1.8 * cm, width, 1.8 * cm, stroke=0, fill=1)
        if LOGO_PATH.exists():
            try:
                logo = RLImage(str(LOGO_PATH), width=2.8 * cm, height=0.53 * cm)
                logo.drawOn(c, 2 * cm, height - 1.2 * cm)
            except Exception:
                pass
        c.setFillColor(WHITE)
        c.setFont('Helvetica', 9)
        c.drawRightString(width - 2 * cm, height - 1.15 * cm,
                          f"Relatório Mensal · {self.mes_extenso}")
        c.setFillColor(BRAND_RED)
        c.rect(0, height - 1.85 * cm, width, 0.05 * cm, stroke=0, fill=1)

    def _page_footer(self, c, width, height, page_num):
        c.setFillColor(GRAY_500)
        c.setFont('Helvetica', 7.5)
        br_today = datetime.now(ZoneInfo('America/Sao_Paulo')).date()
        c.drawString(2 * cm, 1.2 * cm,
                     f"ONEPAX · Operação Farol de São Tomé · gerado em {br_today.strftime('%d/%m/%Y')}")
        c.drawRightString(width - 2 * cm, 1.2 * cm, f"Página {page_num}")


# ──────────────────────────── BUILDERS DE BLOCOS ────────────────────────────

def _kpi_card(label: str, valor: str, sublinhar: str = '', color=DARK) -> Table:
    valor_para = Paragraph(f'<font color="{color.hexval()}">{valor}</font>', S_KPI_VAL)
    sub = Paragraph(sublinhar, S_KPI_SUB) if sublinhar else Paragraph('&nbsp;', S_KPI_SUB)
    t = Table([
        [Paragraph(label.upper(), S_KPI_LBL)],
        [valor_para],
        [sub],
    ], colWidths=[4.0 * cm], rowHeights=[0.5 * cm, 0.95 * cm, 0.5 * cm])
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.4, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


def _kpi_row(kpis: list[tuple[str, str, str, colors.Color]]) -> Table:
    cards = [[_kpi_card(*k)] for k in kpis]
    # Transposing: row table with each KPI as a column
    row = [[_kpi_card(*k) for k in kpis]]
    t = Table(row, colWidths=[4.0 * cm] * len(kpis), hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    return t


def _delta_paragraph(delta_pct: float | None, contexto: str = '') -> str:
    if delta_pct is None:
        return '<font color="#888">primeira referência</font>'
    sinal = '▲' if delta_pct > 0 else '▼' if delta_pct < 0 else '■'
    cor = '#16A34A' if delta_pct > 0 else '#B91C1C' if delta_pct < 0 else '#666'
    return f'<font color="{cor}">{sinal} {_br_num(abs(delta_pct))}%</font>{(" " + contexto) if contexto else ""}'


def _tabela_top(rows: list[list], headers: list[str], col_widths: list[float], highlight_first: bool = True) -> Table:
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, hAlign='LEFT')
    style = [
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), GRAY_500),
        ('BACKGROUND', (0, 0), (-1, 0), GRAY_100),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, GRAY_300),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), GRAY_900),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, colors.HexColor('#FAFAFA')]),
        ('LINEBELOW', (0, -1), (-1, -1), 0.3, GRAY_300),
    ]
    if highlight_first and len(rows) > 0:
        style.append(('FONT', (0, 1), (-1, 1), 'Helvetica-Bold', 9))
        style.append(('TEXTCOLOR', (0, 1), (0, 1), BRAND_RED))
    t.setStyle(TableStyle(style))
    return t


# ──────────────────────────── PÁGINAS ────────────────────────────

def _pagina_capa_resumo(dados: dict, story: list, tmpdir: Path):
    totais = dados['totais']
    comp = dados['comparativo']

    # Espaço pra capa preta
    story.append(Spacer(1, 5.5 * cm))
    story.append(Paragraph('Relatório Mensal de Operações', S_H1))
    story.append(Paragraph(
        f"Período de análise: {date.fromisoformat(dados['periodo']['inicio']).strftime('%d/%m/%Y')} a "
        f"{date.fromisoformat(dados['periodo']['fim']).strftime('%d/%m/%Y')}",
        S_BODY,
    ))
    story.append(Spacer(1, 8))

    # KPIs principais
    story.append(_kpi_row([
        ('Passageiros', _br_num(totais['pax']),
         _delta_paragraph(comp['delta_pax_pct'], 'vs mês anterior'), DARK),
        ('Voos totais', _br_num(totais['voos']),
         _delta_paragraph(comp['delta_voos_pct']), DARK),
        ('Pax / voo', _br_num(totais['pax_por_voo']),
         f"{_br_num(totais['voos_embarque'])} EMB · {_br_num(totais['voos_desembarque'])} DES", DARK),
    ]))
    story.append(Spacer(1, 14))

    # Resumo Executivo (3-4 insights principais)
    story.append(Paragraph('Resumo Executivo', S_H2))
    for ins in dados['insights'][:4]:
        story.append(Paragraph(f'• {ins}', S_INSIGHT))

    story.append(Spacer(1, 8))
    # Comparativo geral
    story.append(Paragraph('Mês a mês', S_H3))
    comp_table = Table([
        ['Métrica', dados['mes_extenso'].capitalize(), comp['mes_anterior_extenso'].capitalize(), 'Variação'],
        ['Passageiros', _br_num(totais['pax']), _br_num(comp['pax_anterior']),
         Paragraph(_delta_paragraph(comp['delta_pax_pct']), S_BODY)],
        ['Voos', _br_num(totais['voos']), _br_num(comp['voos_anterior']),
         Paragraph(_delta_paragraph(comp['delta_voos_pct']), S_BODY)],
    ], colWidths=[3.8 * cm, 3.8 * cm, 3.8 * cm, 4.4 * cm])
    comp_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), GRAY_500),
        ('BACKGROUND', (0, 0), (-1, 0), GRAY_100),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, GRAY_300),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 9.5),
        ('TEXTCOLOR', (0, 1), (-1, -1), GRAY_900),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, -1), (-1, -1), 0.3, GRAY_300),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(comp_table)


def _pagina_volume(dados: dict, story: list, tmpdir: Path):
    story.append(Paragraph('Volume e Tendência', S_H2))

    serie = dados['diario']['serie']
    chart_path = tmpdir / 'chart_diario.png'
    _chart_bar_diario(serie, str(chart_path))
    story.append(RLImage(str(chart_path), width=16.8 * cm, height=5.2 * cm))
    story.append(Spacer(1, 6))

    # Estatísticas
    diario = dados['diario']
    dia_pico = diario['dia_pico']
    dia_menor = diario['dia_menor']
    pico_data = date.fromisoformat(dia_pico['data']).strftime('%d/%m') if dia_pico else '—'
    pico_total = _br_num(dia_pico['total']) if dia_pico else ''
    menor_data = date.fromisoformat(dia_menor['data']).strftime('%d/%m') if dia_menor else '—'
    menor_total = _br_num(dia_menor['total']) if dia_menor else ''

    story.append(_kpi_row([
        ('Média diária', f"{_br_num(diario['media'])} pax", '', DARK),
        ('Mediana', f"{_br_num(diario['mediana'])} pax", '', DARK),
        ('Dia de pico', pico_data, f"{pico_total} pax", GREEN),
        ('Dia mais fraco', menor_data, f"{menor_total} pax", RED_ALERT),
    ]))
    story.append(Spacer(1, 12))

    # Dia da semana
    story.append(Paragraph('Movimento por dia da semana', S_H3))
    chart_dia = tmpdir / 'chart_dia_semana.png'
    _chart_dia_semana(dados['dia_semana']['pax_media'], str(chart_dia), width_in=7.2, height_in=2.2)
    story.append(RLImage(str(chart_dia), width=16.8 * cm, height=5.0 * cm))

    story.append(Spacer(1, 8))
    if diario['dias_acima_media'] > 0 or diario['dias_abaixo_media'] > 0:
        story.append(Paragraph('Outliers do mês', S_H3))
        story.append(Paragraph(
            f"<b>{diario['dias_acima_media']}</b> dia(s) com volume acima de 1,5× a média diária "
            f"e <b>{diario['dias_abaixo_media']}</b> dia(s) abaixo de 0,5× a média — "
            f"sinalizam picos e vales operacionais que merecem atenção.",
            S_BODY,
        ))


def _pagina_operadoras_clientes(dados: dict, story: list, tmpdir: Path):
    story.append(Paragraph('Operadoras e Clientes Finais', S_H2))

    # Donut + tabela lado a lado
    donut_path = tmpdir / 'donut_op.png'
    _chart_donut_operadoras(dados['operadoras'], str(donut_path))

    op_rows = [
        [o['nome'], _br_num(o['passageiros']), _br_num(o['voos']), f"{_br_num(o['pct'])}%"]
        for o in dados['operadoras'][:8]
    ]
    op_table = _tabela_top(
        op_rows,
        headers=['Operadora', 'Pax', 'Voos', '%'],
        col_widths=[5.0 * cm, 2.0 * cm, 1.6 * cm, 1.6 * cm],
    )

    lado_a_lado = Table(
        [[RLImage(str(donut_path), width=6.8 * cm, height=5.0 * cm), op_table]],
        colWidths=[7.0 * cm, 10.5 * cm],
    )
    lado_a_lado.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(lado_a_lado)

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Concentração de operadoras: <b>HHI {int(dados['hhi_operadoras'])}</b> "
        f"({_classificar_concentracao_label(dados['hhi_operadoras'])}). "
        f"HHI mede concentração de mercado: &gt; 2.500 indica alta concentração.",
        S_SMALL,
    ))

    story.append(Spacer(1, 14))
    story.append(Paragraph('Top clientes finais', S_H3))
    cli_rows = [
        [c['nome'], _br_num(c['passageiros']), _br_num(c['voos']), f"{_br_num(c['pct'])}%"]
        for c in dados['clientes'][:8]
    ]
    story.append(_tabela_top(
        cli_rows,
        headers=['Cliente Final', 'Pax', 'Voos', '%'],
        col_widths=[8.0 * cm, 3.0 * cm, 2.5 * cm, 2.5 * cm],
    ))

    story.append(Spacer(1, 12))
    # Comparativo mês anterior — operadoras
    story.append(Paragraph(f"Variação vs {dados['comparativo']['mes_anterior_extenso']}", S_H3))
    comp_rows = []
    for o in dados['comparativo']['operadoras']:
        delta = o['delta_pct']
        if delta is None:
            delta_txt = '—'
        else:
            sinal = '▲' if delta > 0 else '▼' if delta < 0 else '■'
            cor = '#16A34A' if delta > 0 else '#B91C1C' if delta < 0 else '#666'
            delta_txt = Paragraph(
                f'<font color="{cor}">{sinal} {_br_num(abs(delta))}%</font>',
                S_BODY,
            )
        comp_rows.append([o['nome'], _br_num(o['atual']), _br_num(o['anterior']), delta_txt])
    if comp_rows:
        story.append(_tabela_top(
            comp_rows,
            headers=['Operadora', 'Mês atual', 'Mês anterior', 'Variação'],
            col_widths=[5.0 * cm, 3.2 * cm, 3.6 * cm, 3.2 * cm],
            highlight_first=False,
        ))


def _pagina_operacional(dados: dict, story: list, tmpdir: Path):
    story.append(Paragraph('Operacional', S_H2))

    # Horário de pico
    chart_hora = tmpdir / 'chart_hora.png'
    _chart_hora(dados['hora_pax'], str(chart_hora), width_in=7.2, height_in=2.2)
    story.append(Paragraph('Distribuição por hora do dia', S_H3))
    story.append(RLImage(str(chart_hora), width=16.8 * cm, height=5.0 * cm))

    story.append(Spacer(1, 10))

    # Top aeronaves
    story.append(Paragraph('Aeronaves mais utilizadas', S_H3))
    aero_rows = [
        [a['matricula'], _br_num(a['voos']), _br_num(a['passageiros'])]
        for a in dados['aeronaves'][:8]
    ]
    aero_table = _tabela_top(
        aero_rows,
        headers=['Matrícula', 'Voos', 'Pax transportados'],
        col_widths=[3.5 * cm, 2.5 * cm, 4.0 * cm],
    )

    # Top plataformas
    plat_rows = [
        [p['nome'], _br_num(p['voos']), _br_num(p['passageiros'])]
        for p in dados['plataformas'][:8]
    ]
    plat_table = _tabela_top(
        plat_rows,
        headers=['Plataforma (Emb.)', 'Voos', 'Pax'],
        col_widths=[3.5 * cm, 2.0 * cm, 2.5 * cm],
    )

    story.append(Table(
        [[aero_table, plat_table]],
        colWidths=[10.0 * cm, 8.0 * cm],
        style=TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]),
    ))

    story.append(Spacer(1, 10))
    # Top origens (desembarque)
    if dados['origens']:
        story.append(Paragraph('Origens de desembarque', S_H3))
        orig_rows = [
            [o['nome'], _br_num(o['voos']), _br_num(o['passageiros'])]
            for o in dados['origens'][:8]
        ]
        story.append(_tabela_top(
            orig_rows,
            headers=['Origem', 'Voos', 'Pax'],
            col_widths=[8.0 * cm, 3.0 * cm, 4.0 * cm],
        ))


def _pagina_insights(dados: dict, story: list, tmpdir: Path):
    story.append(Paragraph('Insights da Operação', S_H2))
    story.append(Paragraph(
        'Análises derivadas exclusivamente dos registros de embarque e desembarque do mês.',
        S_SMALL,
    ))
    story.append(Spacer(1, 10))

    for i, ins in enumerate(dados['insights'], start=1):
        story.append(Paragraph(f'<b>{i:02d}.</b> {ins}', S_INSIGHT))

    story.append(Spacer(1, 18))
    # Glossário breve
    story.append(Paragraph('Notas metodológicas', S_H3))
    story.append(Paragraph(
        '<b>HHI</b> (Herfindahl–Hirschman Index): mede concentração de mercado. '
        'Soma dos quadrados dos market shares × 100. Valores típicos: '
        '&lt; 1.500 baixa concentração, 1.500–2.500 moderada, &gt; 2.500 alta.',
        S_SMALL,
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        '<b>Outliers</b>: classificamos como dia de pico os dias com volume ≥ 1,5× a média, '
        'e dias de vale aqueles com volume ≤ 0,5× a média (excluindo dias sem operação).',
        S_SMALL,
    ))


def _classificar_concentracao_label(hhi: float) -> str:
    if hhi >= 2500:
        return 'concentração alta'
    if hhi >= 1500:
        return 'concentração moderada'
    return 'concentração baixa'


# ──────────────────────────── ENTRY POINT ────────────────────────────

def gerar_pdf_relatorio_mensal(dados: dict, tmpdir: Path) -> bytes:
    """Gera o PDF do relatório mensal a partir dos dados já agregados.
    Retorna bytes do PDF.
    """
    tmpdir = Path(tmpdir)
    tmpdir.mkdir(parents=True, exist_ok=True)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.4 * cm,
        bottomMargin=2 * cm,
        title=f"Relatório Mensal ONEPAX - {dados['mes_extenso']}",
        author='ONEPAX',
    )

    story = []
    _pagina_capa_resumo(dados, story, tmpdir)
    story.append(PageBreak())
    _pagina_volume(dados, story, tmpdir)
    story.append(PageBreak())
    _pagina_operadoras_clientes(dados, story, tmpdir)
    story.append(PageBreak())
    _pagina_operacional(dados, story, tmpdir)
    story.append(PageBreak())
    _pagina_insights(dados, story, tmpdir)

    decorator = _PageDecorator(dados['mes_extenso'], dados['periodo'])
    doc.build(story, onFirstPage=decorator, onLaterPages=decorator)

    return buf.getvalue()
