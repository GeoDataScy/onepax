"""
Agregações e insights para o relatório mensal operacional do ONEPAX.

Tudo aqui consulta exclusivamente os modelos Embarque e Desembarque.
Nenhum valor é inferido fora dos dados reais do banco.
"""
from calendar import monthrange
from datetime import date, timedelta
from collections import Counter

from django.db.models import Sum, Count, Avg

from operacao_voo.models import Embarque, Desembarque


_MESES_PT = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
             'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

_DIAS_SEMANA_PT = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']


def _br_num(n: float | int) -> str:
    """Formata número no padrão brasileiro (10.000 e 12,5)."""
    if isinstance(n, float) and n != int(n):
        s = f"{n:,.1f}"
    else:
        s = f"{int(n):,}"
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def mes_extenso(ano: int, mes: int) -> str:
    return f"{_MESES_PT[mes - 1]} de {ano}"


def _range_mes(ano: int, mes: int) -> tuple[date, date]:
    primeiro = date(ano, mes, 1)
    ultimo = date(ano, mes, monthrange(ano, mes)[1])
    return primeiro, ultimo


def _normalizar(valor) -> str:
    if not valor:
        return 'Não informado'
    s = str(valor).strip()
    return s if s else 'Não informado'


def _pct(parte: float, total: float) -> float:
    return round((parte / total) * 100, 1) if total else 0.0


def _hhi(valores: list[int]) -> float:
    """Herfindahl–Hirschman Index normalizado para 0–10.000.
    Mede concentração: >2.500 = alta, 1.500–2.500 = moderada, <1.500 = baixa."""
    total = sum(valores)
    if not total:
        return 0.0
    shares = [(v / total) * 100 for v in valores]
    return round(sum(s ** 2 for s in shares), 0)


def _classificar_concentracao(hhi: float) -> str:
    if hhi >= 2500:
        return 'alta'
    if hhi >= 1500:
        return 'moderada'
    return 'baixa'


def gerar_dados_relatorio_mensal(ano: int, mes: int) -> dict:
    """Devolve dict completo com todas as agregações e insights do mês."""
    primeiro, ultimo = _range_mes(ano, mes)
    dias_no_mes = (ultimo - primeiro).days + 1

    emb_qs = Embarque.objects.filter(departure_date__gte=primeiro, departure_date__lte=ultimo)
    des_qs = Desembarque.objects.filter(arrival_date__gte=primeiro, arrival_date__lte=ultimo)

    # === Totais ===
    total_emb_pax = emb_qs.aggregate(t=Sum('passengers_boarded'))['t'] or 0
    total_des_pax = des_qs.aggregate(t=Sum('passengers_disembarked'))['t'] or 0
    total_pax = total_emb_pax + total_des_pax
    voos_emb = emb_qs.count()
    voos_des = des_qs.count()
    total_voos = voos_emb + voos_des
    pax_por_voo = round(total_pax / total_voos, 1) if total_voos else 0.0

    # === Pax por dia ===
    pax_por_dia: dict[str, dict] = {}
    for i in range(dias_no_mes):
        d = (primeiro + timedelta(days=i)).isoformat()
        pax_por_dia[d] = {'data': d, 'embarque': 0, 'desembarque': 0, 'total': 0}

    for row in emb_qs.values('departure_date').annotate(t=Sum('passengers_boarded')):
        d = row['departure_date'].isoformat()
        pax_por_dia[d]['embarque'] = row['t'] or 0
    for row in des_qs.values('arrival_date').annotate(t=Sum('passengers_disembarked')):
        d = row['arrival_date'].isoformat()
        pax_por_dia[d]['desembarque'] = row['t'] or 0
    for d in pax_por_dia:
        pax_por_dia[d]['total'] = pax_por_dia[d]['embarque'] + pax_por_dia[d]['desembarque']

    serie_diaria = list(pax_por_dia.values())
    totais_diarios = [d['total'] for d in serie_diaria]
    media_diaria = round(sum(totais_diarios) / len(totais_diarios), 1) if totais_diarios else 0.0
    ordenado = sorted(totais_diarios)
    mediana_diaria = ordenado[len(ordenado) // 2] if ordenado else 0
    max_diario = max(totais_diarios) if totais_diarios else 0
    min_diario = min(totais_diarios) if totais_diarios else 0

    # Dia mais movimentado / menos movimentado (entre dias com movimento)
    dias_com_mov = [d for d in serie_diaria if d['total'] > 0]
    dia_pico = max(dias_com_mov, key=lambda x: x['total']) if dias_com_mov else None
    dia_menor = min(dias_com_mov, key=lambda x: x['total']) if dias_com_mov else None

    # Outliers (1.5x acima da média = pico, abaixo de 0.5x = vale)
    threshold_alto = media_diaria * 1.5 if media_diaria else 0
    threshold_baixo = media_diaria * 0.5 if media_diaria else 0
    dias_pico = [d for d in dias_com_mov if d['total'] >= threshold_alto] if threshold_alto else []
    dias_vale = [d for d in dias_com_mov if 0 < d['total'] <= threshold_baixo] if threshold_baixo else []

    # === Distribuição por dia da semana ===
    dias_semana_count = [0] * 7
    dias_semana_pax = [0] * 7
    for item in serie_diaria:
        d_obj = date.fromisoformat(item['data'])
        if item['total'] > 0:
            dias_semana_count[d_obj.weekday()] += 1
            dias_semana_pax[d_obj.weekday()] += item['total']
    media_pax_por_dia_semana = [
        round(dias_semana_pax[i] / dias_semana_count[i], 1) if dias_semana_count[i] else 0
        for i in range(7)
    ]

    # === Distribuição por hora do dia ===
    hora_pax = [0] * 24
    for row in emb_qs.values('departure_time').annotate(t=Sum('passengers_boarded')):
        if row['departure_time']:
            hora_pax[row['departure_time'].hour] += row['t'] or 0
    for row in des_qs.values('arrival_time').annotate(t=Sum('passengers_disembarked')):
        if row['arrival_time']:
            hora_pax[row['arrival_time'].hour] += row['t'] or 0

    # === Operadoras ===
    op_emb = {row['operadora']: row['t'] or 0 for row in emb_qs.values('operadora').annotate(t=Sum('passengers_boarded'))}
    op_des = {row['operadora']: row['t'] or 0 for row in des_qs.values('operadora').annotate(t=Sum('passengers_disembarked'))}
    op_voos = Counter()
    for row in emb_qs.values('operadora').annotate(c=Count('id')):
        op_voos[_normalizar(row['operadora'])] += row['c']
    for row in des_qs.values('operadora').annotate(c=Count('id')):
        op_voos[_normalizar(row['operadora'])] += row['c']

    op_total: dict[str, int] = {}
    for op, v in op_emb.items():
        op_total[_normalizar(op)] = op_total.get(_normalizar(op), 0) + v
    for op, v in op_des.items():
        op_total[_normalizar(op)] = op_total.get(_normalizar(op), 0) + v

    top_operadoras = sorted(op_total.items(), key=lambda kv: -kv[1])
    operadoras_payload = [
        {
            'nome': nome,
            'passageiros': pax,
            'voos': op_voos[nome],
            'pct': _pct(pax, total_pax),
        }
        for nome, pax in top_operadoras
    ]
    hhi_operadoras = _hhi([pax for _, pax in top_operadoras])

    # === Clientes finais ===
    cli_total: dict[str, int] = {}
    cli_voos: Counter = Counter()
    for row in emb_qs.values('cliente_final').annotate(t=Sum('passengers_boarded'), c=Count('id')):
        nome = _normalizar(row['cliente_final'])
        cli_total[nome] = cli_total.get(nome, 0) + (row['t'] or 0)
        cli_voos[nome] += row['c']
    for row in des_qs.values('cliente_final').annotate(t=Sum('passengers_disembarked'), c=Count('id')):
        nome = _normalizar(row['cliente_final'])
        cli_total[nome] = cli_total.get(nome, 0) + (row['t'] or 0)
        cli_voos[nome] += row['c']
    top_clientes_raw = sorted(cli_total.items(), key=lambda kv: -kv[1])
    clientes_payload = [
        {'nome': nome, 'passageiros': pax, 'voos': cli_voos[nome], 'pct': _pct(pax, total_pax)}
        for nome, pax in top_clientes_raw
    ]
    hhi_clientes = _hhi([pax for _, pax in top_clientes_raw])

    # === Aeronaves ===
    aero_total: dict[str, dict] = {}
    for row in emb_qs.values('aeronave').annotate(t=Sum('passengers_boarded'), c=Count('id')):
        nome = _normalizar(row['aeronave'])
        a = aero_total.setdefault(nome, {'pax': 0, 'voos': 0})
        a['pax'] += row['t'] or 0
        a['voos'] += row['c']
    for row in des_qs.values('aeronave').annotate(t=Sum('passengers_disembarked'), c=Count('id')):
        nome = _normalizar(row['aeronave'])
        a = aero_total.setdefault(nome, {'pax': 0, 'voos': 0})
        a['pax'] += row['t'] or 0
        a['voos'] += row['c']
    top_aeronaves = sorted(aero_total.items(), key=lambda kv: -kv[1]['voos'])
    aeronaves_payload = [
        {'matricula': nome, 'passageiros': v['pax'], 'voos': v['voos']}
        for nome, v in top_aeronaves
    ]

    # === Plataformas (embarque) ===
    plat_total: dict[str, dict] = {}
    for row in emb_qs.values('platform').annotate(t=Sum('passengers_boarded'), c=Count('id')):
        nome = _normalizar(row['platform'])
        plat_total[nome] = {'pax': row['t'] or 0, 'voos': row['c']}
    top_plataformas = sorted(plat_total.items(), key=lambda kv: -kv[1]['pax'])
    plataformas_payload = [
        {'nome': nome, 'passageiros': v['pax'], 'voos': v['voos']}
        for nome, v in top_plataformas
    ]

    # === Origens (desembarque) ===
    orig_total: dict[str, dict] = {}
    for row in des_qs.values('origin').annotate(t=Sum('passengers_disembarked'), c=Count('id')):
        nome = _normalizar(row['origin'])
        orig_total[nome] = {'pax': row['t'] or 0, 'voos': row['c']}
    top_origens = sorted(orig_total.items(), key=lambda kv: -kv[1]['pax'])
    origens_payload = [
        {'nome': nome, 'passageiros': v['pax'], 'voos': v['voos']}
        for nome, v in top_origens
    ]

    # === Comparativo com mês anterior ===
    if mes == 1:
        ano_prev, mes_prev = ano - 1, 12
    else:
        ano_prev, mes_prev = ano, mes - 1
    prev_primeiro, prev_ultimo = _range_mes(ano_prev, mes_prev)
    prev_emb = Embarque.objects.filter(departure_date__gte=prev_primeiro, departure_date__lte=prev_ultimo)
    prev_des = Desembarque.objects.filter(arrival_date__gte=prev_primeiro, arrival_date__lte=prev_ultimo)
    prev_total_pax = (prev_emb.aggregate(t=Sum('passengers_boarded'))['t'] or 0) + \
                     (prev_des.aggregate(t=Sum('passengers_disembarked'))['t'] or 0)
    prev_voos = prev_emb.count() + prev_des.count()

    def _delta_pct(atual, anterior):
        if not anterior:
            return None
        return round(((atual - anterior) / anterior) * 100, 1)

    delta_pax = _delta_pct(total_pax, prev_total_pax)
    delta_voos = _delta_pct(total_voos, prev_voos)

    # Comparativo por operadora (top 5)
    prev_op_total: dict[str, int] = {}
    for row in prev_emb.values('operadora').annotate(t=Sum('passengers_boarded')):
        prev_op_total[_normalizar(row['operadora'])] = prev_op_total.get(_normalizar(row['operadora']), 0) + (row['t'] or 0)
    for row in prev_des.values('operadora').annotate(t=Sum('passengers_disembarked')):
        prev_op_total[_normalizar(row['operadora'])] = prev_op_total.get(_normalizar(row['operadora']), 0) + (row['t'] or 0)
    operadoras_comparativo = []
    for nome, pax in top_operadoras[:5]:
        anterior = prev_op_total.get(nome, 0)
        operadoras_comparativo.append({
            'nome': nome,
            'atual': pax,
            'anterior': anterior,
            'delta_pct': _delta_pct(pax, anterior),
        })

    # === Insights textuais auto-gerados ===
    insights: list[str] = []

    if total_pax == 0:
        insights.append(f"Nenhum movimento registrado em {mes_extenso(ano, mes)}.")
    else:
        insights.append(
            f"Em {mes_extenso(ano, mes)} foram transportados {_br_num(total_pax)} passageiros "
            f"em {_br_num(total_voos)} voos, com média de {_br_num(pax_por_voo)} pax/voo."
        )

        if delta_pax is not None:
            direcao = 'crescimento' if delta_pax > 0 else 'queda' if delta_pax < 0 else 'estabilidade'
            sinal = '+' if delta_pax > 0 else ''
            insights.append(
                f"Comparado a {mes_extenso(ano_prev, mes_prev)} ({_br_num(prev_total_pax)} pax), "
                f"houve {direcao} de {sinal}{_br_num(delta_pax)}%."
            )

        if dia_pico:
            d_obj = date.fromisoformat(dia_pico['data'])
            insights.append(
                f"O dia mais movimentado foi {d_obj.strftime('%d/%m')} "
                f"({_DIAS_SEMANA_PT[d_obj.weekday()].lower()}) "
                f"com {_br_num(dia_pico['total'])} passageiros — "
                f"{_br_num(round(dia_pico['total'] / media_diaria, 1))}x a média diária."
            )

        if operadoras_payload:
            lider = operadoras_payload[0]
            insights.append(
                f"{lider['nome']} liderou a operação com {_br_num(lider['pct'])}% do tráfego "
                f"({_br_num(lider['passageiros'])} pax em {_br_num(lider['voos'])} voos)."
            )

        if len(operadoras_payload) >= 2:
            top3_share = sum(o['pct'] for o in operadoras_payload[:3])
            insights.append(
                f"Concentração de operadoras: as 3 maiores responderam por {_br_num(round(top3_share, 1))}% "
                f"do movimento (HHI={int(hhi_operadoras)}, "
                f"{_classificar_concentracao(hhi_operadoras)})."
            )

        if clientes_payload:
            lider_cli = clientes_payload[0]
            insights.append(
                f"O cliente final com maior demanda foi {lider_cli['nome']} "
                f"({_br_num(lider_cli['passageiros'])} pax, {_br_num(lider_cli['pct'])}% do total)."
            )

        if dias_pico:
            insights.append(
                f"{len(dias_pico)} dia(s) ficaram acima de 1,5x a média diária — "
                f"picos de demanda concentrada."
            )

        # Dia da semana mais forte
        if any(media_pax_por_dia_semana):
            idx_max = max(range(7), key=lambda i: media_pax_por_dia_semana[i])
            nome_dia = _DIAS_SEMANA_PT[idx_max]
            sufixo = 's-feiras' if idx_max < 5 else 's'
            insights.append(
                f"Em média, {nome_dia}{sufixo} "
                f"foram os dias com maior movimento "
                f"({_br_num(round(media_pax_por_dia_semana[idx_max]))} pax/dia)."
            )

        # Pico de horário
        if any(hora_pax):
            idx_h = max(range(24), key=lambda i: hora_pax[i])
            insights.append(
                f"O horário de pico foi entre {idx_h:02d}h e {idx_h + 1:02d}h "
                f"({_br_num(hora_pax[idx_h])} pax acumulados no mês)."
            )

        # Comparativo destaque
        crescimentos = [o for o in operadoras_comparativo if o['delta_pct'] is not None]
        if crescimentos:
            destaque = max(crescimentos, key=lambda o: o['delta_pct'] or 0)
            if destaque['delta_pct'] is not None and destaque['delta_pct'] > 0:
                insights.append(
                    f"Maior crescimento entre as top 5 operadoras: {destaque['nome']} "
                    f"(+{_br_num(destaque['delta_pct'])}% vs mês anterior)."
                )

    return {
        'ano': ano,
        'mes': mes,
        'mes_extenso': mes_extenso(ano, mes),
        'periodo': {'inicio': primeiro.isoformat(), 'fim': ultimo.isoformat()},
        'dias_no_mes': dias_no_mes,
        'totais': {
            'pax': total_pax,
            'pax_embarcados': total_emb_pax,
            'pax_desembarcados': total_des_pax,
            'voos': total_voos,
            'voos_embarque': voos_emb,
            'voos_desembarque': voos_des,
            'pax_por_voo': pax_por_voo,
        },
        'diario': {
            'serie': serie_diaria,
            'media': media_diaria,
            'mediana': mediana_diaria,
            'max': max_diario,
            'min': min_diario,
            'dia_pico': dia_pico,
            'dia_menor': dia_menor,
            'dias_acima_media': len(dias_pico),
            'dias_abaixo_media': len(dias_vale),
        },
        'dia_semana': {
            'labels': _DIAS_SEMANA_PT,
            'voos_count': dias_semana_count,
            'pax_total': dias_semana_pax,
            'pax_media': media_pax_por_dia_semana,
        },
        'hora_pax': hora_pax,
        'operadoras': operadoras_payload,
        'hhi_operadoras': hhi_operadoras,
        'clientes': clientes_payload,
        'hhi_clientes': hhi_clientes,
        'aeronaves': aeronaves_payload,
        'plataformas': plataformas_payload,
        'origens': origens_payload,
        'comparativo': {
            'mes_anterior_extenso': mes_extenso(ano_prev, mes_prev),
            'pax_anterior': prev_total_pax,
            'voos_anterior': prev_voos,
            'delta_pax_pct': delta_pax,
            'delta_voos_pct': delta_voos,
            'operadoras': operadoras_comparativo,
        },
        'insights': insights,
    }
