"""
main.py — Servidor FastAPI.

Rodar:
    uvicorn main:app --reload

Acessar:
    http://127.0.0.1:8000
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

import models
import kmeans as km
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()   # cria as tabelas ao iniciar
    yield


app = FastAPI(title="FinançasClusters API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════
#  FRONTEND
# ══════════════════════════════════════════════════════════

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def raiz():
    return FileResponse("static/index.html")

@app.get("/transacoes", include_in_schema=False)
def pagina_transacoes():
    return FileResponse("static/transacoes.html")

@app.get("/relatorio", include_in_schema=False)
def pagina_relatorio():
    return FileResponse("static/relatorio.html")

@app.get("/clusters", include_in_schema=False)
def pagina_clusters():
    return FileResponse("static/clusters.html")


# ══════════════════════════════════════════════════════════
#  SCHEMAS
# ══════════════════════════════════════════════════════════

class TransacaoIn(BaseModel):
    tipo:      str
    descricao: str
    valor:     float
    mes:       int
    ano:       int


# ══════════════════════════════════════════════════════════
#  API — TRANSAÇÕES
# ══════════════════════════════════════════════════════════

@app.get("/api/transacoes", tags=["Transações"])
def api_listar(mes: Optional[int]=None, ano: Optional[int]=None, tipo: Optional[str]=None):
    return models.listar_transacoes(mes=mes, ano=ano, tipo=tipo)

@app.post("/api/transacoes", status_code=201, tags=["Transações"])
def api_criar(body: TransacaoIn):
    if body.tipo not in ("ganho", "gasto"):
        raise HTTPException(400, "tipo deve ser 'ganho' ou 'gasto'")
    if body.valor <= 0:
        raise HTTPException(400, "valor deve ser positivo")
    if not 1 <= body.mes <= 12:
        raise HTTPException(400, "mes deve ser entre 1 e 12")
    if not body.descricao.strip():
        raise HTTPException(400, "descricao não pode estar vazia")
    new_id = models.criar_transacao(body.tipo, body.descricao.strip(), body.valor, body.mes, body.ano)
    return {"id": new_id, "mensagem": "Transação criada com sucesso."}

@app.put("/api/transacoes/{id}", tags=["Transações"])
def api_atualizar(id: int, body: TransacaoIn):
    if not models.buscar_transacao(id):
        raise HTTPException(404, "Transação não encontrada")
    if body.tipo not in ("ganho", "gasto"):
        raise HTTPException(400, "tipo deve ser 'ganho' ou 'gasto'")
    if body.valor <= 0:
        raise HTTPException(400, "valor deve ser positivo")
    models.atualizar_transacao(id, body.tipo, body.descricao.strip(), body.valor, body.mes, body.ano)
    return {"mensagem": "Transação atualizada."}

@app.delete("/api/transacoes/{id}", tags=["Transações"])
def api_deletar(id: int):
    if not models.buscar_transacao(id):
        raise HTTPException(404, "Transação não encontrada")
    models.deletar_transacao(id)
    return {"mensagem": "Transação removida."}


# ══════════════════════════════════════════════════════════
#  API — RELATÓRIO
# ══════════════════════════════════════════════════════════

@app.get("/api/relatorio", tags=["Relatório"])
def api_relatorio(mes: Optional[int]=None, ano: Optional[int]=None):
    hoje = datetime.now()
    return models.relatorio_mensal(mes or hoje.month, ano or hoje.year)

@app.get("/api/anos", tags=["Relatório"])
def api_anos():
    return models.anos_disponiveis()


# ══════════════════════════════════════════════════════════
#  API — K-MEANS
# ══════════════════════════════════════════════════════════

@app.get("/api/clusters", tags=["K-Means"])
def api_clusters(tipo: str = "gasto", k: int = 3):
    if tipo not in ("ganho", "gasto"):
        raise HTTPException(400, "tipo deve ser 'ganho' ou 'gasto'")
    if not 2 <= k <= 8:
        raise HTTPException(400, "k deve ser entre 2 e 8")

    transacoes = models.listar_transacoes(tipo=tipo)
    minimo = max(k, 3)
    if len(transacoes) < minimo:
        raise HTTPException(400, f"Cadastre pelo menos {minimo} transações do tipo '{tipo}'.")

    try:
        dados_orig = [[t["valor"], float(t["mes"])] for t in transacoes]
        dados_norm, _ = km.normalizar(dados_orig)

        centroides, atribuicoes, inercia, n_iter, _ = km.kmeans(dados_norm, k)
        perfis   = km.rotular_clusters(dados_orig, atribuicoes, k)
        cotovelo = km.metodo_cotovelo(dados_norm, k_max=min(8, len(transacoes)))
    except Exception as e:
        raise HTTPException(500, f"Erro ao executar K-Means: {str(e)}")

    grupos = {str(cid): [] for cid in range(k)}
    for i, t in enumerate(transacoes):
        grupos[str(atribuicoes[i])].append(t)

    return {
        "k":        k,
        "tipo":     tipo,
        "inercia":  round(inercia, 4),
        "n_iter":   n_iter,
        "grupos":   grupos,
        "perfis":   {str(cid): v for cid, v in perfis.items()},
        "cotovelo": cotovelo,
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)
