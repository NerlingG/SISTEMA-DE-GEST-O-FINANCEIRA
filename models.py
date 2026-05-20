from database import get_connection


# ══════════════════════════════════════════════════════════
#  TRANSAÇÕES — CRUD
# ══════════════════════════════════════════════════════════

def criar_transacao(tipo, descricao, valor, mes, ano):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO transacoes (tipo, descricao, valor, mes, ano) VALUES (%s,%s,%s,%s,%s)",
        (tipo, descricao, float(valor), int(mes), int(ano))
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close(); conn.close()
    return new_id


def listar_transacoes(mes=None, ano=None, tipo=None):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    sql, params = "SELECT * FROM transacoes WHERE 1=1", []
    if mes:  sql += " AND mes=%s";  params.append(int(mes))
    if ano:  sql += " AND ano=%s";  params.append(int(ano))
    if tipo: sql += " AND tipo=%s"; params.append(tipo)
    sql += " ORDER BY ano DESC, mes DESC, criado_em DESC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close(); conn.close()
    # Converte Decimal → float e datetime → str
    for r in rows:
        r["valor"] = float(r["valor"])
        if r.get("criado_em"): r["criado_em"] = str(r["criado_em"])
    return rows


def buscar_transacao(id):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM transacoes WHERE id=%s", (id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if row:
        row["valor"] = float(row["valor"])
        if row.get("criado_em"): row["criado_em"] = str(row["criado_em"])
    return row


def atualizar_transacao(id, tipo, descricao, valor, mes, ano):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE transacoes SET tipo=%s,descricao=%s,valor=%s,mes=%s,ano=%s WHERE id=%s",
        (tipo, descricao, float(valor), int(mes), int(ano), id)
    )
    conn.commit()
    cur.close(); conn.close()


def deletar_transacao(id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM transacoes WHERE id=%s", (id,))
    conn.commit()
    cur.close(); conn.close()


# ══════════════════════════════════════════════════════════
#  RELATÓRIO MENSAL
# ══════════════════════════════════════════════════════════

def relatorio_mensal(mes, ano):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    mes, ano = int(mes), int(ano)

    cur.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN tipo='ganho' THEN valor END),0) AS total_ganhos,
            COALESCE(SUM(CASE WHEN tipo='gasto' THEN valor END),0) AS total_gastos
        FROM transacoes WHERE mes=%s AND ano=%s
    """, (mes, ano))
    t = cur.fetchone()
    tg = float(t["total_ganhos"])
    tgs = float(t["total_gastos"])

    # Evolução 7 meses (6 anteriores + atual)
    meses_ant = []
    m, a = mes, ano
    for _ in range(6):
        m -= 1
        if m == 0: m, a = 12, a - 1
        meses_ant.append((m, a))

    evolucao = []
    for m_a, a_a in reversed(meses_ant):
        cur.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo='ganho' THEN valor END),0) AS g,
                COALESCE(SUM(CASE WHEN tipo='gasto' THEN valor END),0) AS gs
            FROM transacoes WHERE mes=%s AND ano=%s
        """, (m_a, a_a))
        r = cur.fetchone()
        evolucao.append({
            "label":  f"{m_a:02d}/{a_a}",
            "ganhos": float(r["g"]),
            "gastos": float(r["gs"]),
            "saldo":  float(r["g"]) - float(r["gs"]),
        })
    evolucao.append({"label": f"{mes:02d}/{ano}", "ganhos": tg, "gastos": tgs, "saldo": tg - tgs})

    cur.execute(
        "SELECT * FROM transacoes WHERE mes=%s AND ano=%s ORDER BY tipo, valor DESC",
        (mes, ano)
    )
    txs = cur.fetchall()
    cur.close(); conn.close()

    for r in txs:
        r["valor"] = float(r["valor"])
        if r.get("criado_em"): r["criado_em"] = str(r["criado_em"])

    return {
        "mes": mes, "ano": ano,
        "total_ganhos": tg,
        "total_gastos": tgs,
        "saldo":        tg - tgs,
        "evolucao":     evolucao,
        "transacoes":   txs,
    }


def anos_disponiveis():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT ano FROM transacoes ORDER BY ano DESC")
    anos = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    return anos or [2025]
