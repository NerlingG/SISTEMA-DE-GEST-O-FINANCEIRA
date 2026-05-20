"""
kmeans.py — K-Means implementado do zero. Sem bibliotecas de ML.
"""
import random
import math


def distancia_euclidiana(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def normalizar(dados):
    n = len(dados[0])
    mins = [min(p[d] for p in dados) for d in range(n)]
    maxs = [max(p[d] for p in dados) for d in range(n)]
    norm = []
    for p in dados:
        novo = []
        for d in range(n):
            amp = maxs[d] - mins[d]
            novo.append((p[d] - mins[d]) / amp if amp else 0.0)
        norm.append(novo)
    return norm, list(zip(mins, maxs))


def inicializar_centroides(dados, k, seed=42):
    random.seed(seed)
    centroides = [list(random.choice(dados))]
    for _ in range(1, k):
        dists = [min(distancia_euclidiana(p, c) ** 2 for c in centroides) for p in dados]
        total = sum(dists)
        if total == 0:
            # todos os pontos são idênticos — escolhe aleatório
            centroides.append(list(random.choice(dados)))
            continue
        probs = [d / total for d in dists]
        acum, r = 0, random.random()
        for ponto, prob in zip(dados, probs):
            acum += prob
            if acum >= r:
                centroides.append(list(ponto))
                break
        if len(centroides) < _ + 1:
            centroides.append(list(dados[-1]))
    return centroides


def atribuir_clusters(dados, centroides):
    return [
        min(range(len(centroides)), key=lambda i: distancia_euclidiana(p, centroides[i]))
        for p in dados
    ]


def recalcular_centroides(dados, atribuicoes, k):
    novos = []
    for cid in range(k):
        pts = [dados[i] for i, a in enumerate(atribuicoes) if a == cid]
        if not pts:
            novos.append(None)
            continue
        novos.append([sum(p[d] for p in pts) / len(pts) for d in range(len(pts[0]))])
    return novos


def calcular_inercia(dados, atribuicoes, centroides):
    return sum(
        distancia_euclidiana(p, centroides[a]) ** 2
        for p, a in zip(dados, atribuicoes)
    )


def convergiram(antigos, novos, tol=1e-6):
    return all(
        n is None or distancia_euclidiana(a, n) < tol
        for a, n in zip(antigos, novos)
    )


def kmeans(dados, k, max_iter=300, tol=1e-6, seed=42):
    if k > len(dados):
        raise ValueError(f"k={k} maior que o número de pontos ({len(dados)}).")
    if k == 1:
        # caso trivial: um único cluster com todos os pontos
        inercia = sum(
            distancia_euclidiana(p, [sum(p[d] for p in dados) / len(dados) for d in range(len(dados[0]))]) ** 2
            for p in dados
        )
        return [[sum(p[d] for p in dados) / len(dados) for d in range(len(dados[0]))]], \
               [0] * len(dados), inercia, 1, [inercia]

    centroides = inicializar_centroides(dados, k, seed)
    historico = []
    n_iter = 0

    for it in range(1, max_iter + 1):
        n_iter = it
        atribuicoes = atribuir_clusters(dados, centroides)
        novos = recalcular_centroides(dados, atribuicoes, k)
        novos = [n if n is not None else centroides[i] for i, n in enumerate(novos)]
        inercia = calcular_inercia(dados, atribuicoes, novos)
        historico.append(inercia)
        if convergiram(centroides, novos, tol):
            centroides = novos
            break
        centroides = novos

    return centroides, atribuicoes, inercia, n_iter, historico


def metodo_cotovelo(dados, k_max=8, seed=42):
    # Limita k ao número de pontos únicos para evitar erros
    unicos = len(set(tuple(p) for p in dados))
    lim = min(k_max, len(dados), unicos, 8)
    resultado = []
    for k in range(1, lim + 1):
        try:
            _, _, inercia, _, _ = kmeans(dados, k, seed=seed)
            resultado.append({"k": k, "inercia": round(inercia, 4)})
        except Exception:
            break
    return resultado


PERFIS = [
    {"nome": "Gastos Cotidianos", "cor": "#4ade80", "emoji": "🟢"},
    {"nome": "Gastos Moderados",  "cor": "#fbbf24", "emoji": "🟡"},
    {"nome": "Gastos Elevados",   "cor": "#f87171", "emoji": "🔴"},
    {"nome": "Cluster 4",         "cor": "#60a5fa", "emoji": "🔵"},
    {"nome": "Cluster 5",         "cor": "#a78bfa", "emoji": "🟣"},
]


def rotular_clusters(dados_orig, atribuicoes, k):
    medias = []
    for cid in range(k):
        vals = [dados_orig[i][0] for i, a in enumerate(atribuicoes) if a == cid]
        medias.append((sum(vals) / len(vals) if vals else 0, cid))
    medias.sort()
    return {cid: PERFIS[rank] for rank, (_, cid) in enumerate(medias)}
