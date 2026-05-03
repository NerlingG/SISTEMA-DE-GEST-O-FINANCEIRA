## Estrutura do projeto

```
sistema-gestao-financeira/
├── main.py          # FastAPI — rotas da API e serve o frontend
├── models.py        # Queries MySQL (CRUD e relatório)
├── database.py      # Conexão e inicialização do banco
├── kmeans.py        # Algoritmo K-Means implementado do zero
├── config.py     # Sistema de Gestão Financeira com K-Means

Sistema web de gestão financeira empresarial com aplicação do algoritmo K-Means implementado do zero para segmentação e análise de dados financeiros.

Projeto Integrador III — Curso de Ciência da Computação  
Universidade Regional Integrada do Alto Uruguai e das Missões — URI Erechim

---

## Sobre o projeto

O sistema permite o cadastro e controle de receitas e despesas de uma organização, aplicando o algoritmo de agrupamento K-Means — desenvolvido manualmente, sem uso de bibliotecas de machine learning — para identificar padrões nos dados financeiros e auxiliar na tomada de decisões estratégicas.

## Funcionalidades

- Cadastro, edição e exclusão de transações financeiras (receitas e despesas)
- Aplicação do algoritmo K-Means do zero para segmentação dos dados
- Visualização dos clusters gerados com gráficos interativos (canvas puro)
- Dashboard com indicadores financeiros do mês
- Relatórios de evolução financeira por período
- Método do Cotovelo para escolha do k ideal
- API REST para comunicação entre frontend e backend

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + FastAPI |
| Banco de dados | MySQL (XAMPP) |
| Algoritmo K-Means | Python puro (sem bibliotecas de ML) |
| Visualização | Canvas API (JavaScript puro) |
| Frontend | HTML + CSS + JavaScript |
| Controle de versão | Git + GitHub |

## Pré-requisitos

- Python 3.10+
- XAMPP com MySQL ativo
- Git

## Como rodar o projeto

**1. Clone o repositório**
```bash
git clone git@github.com:nerlingg/sistema-gest-o-financeira.git
cd sistema-gest-o-financeira
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure o banco de dados**

Edite o arquivo `config.py` na raiz do projeto:
```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "senha123",               
    "database": "gestao_financeira",
    "charset":  "utf8mb4",
}
```

**5. Crie o banco de dados**

Com o XAMPP iniciado, acesse o phpMyAdmin e crie um banco chamado `gestao_financeira`, ou execute:
```sql
CREATE DATABASE gestao_financeira CHARACTER SET utf8mb4;
```

**6. Inicialize as tabelas**
```bash
python database.py
```

**7. Inicie o servidor**
```bash
uvicorn main:app --reload
```
   # Configurações do banco de dados
├── requirements.txt
└── static/          # Frontend (servido pelo FastAPI)
    ├── api.js           # Comunicação com a API via fetch()
    ├── index.html       # Dashboard financeiro
    ├── transacoes.html  # CRUD de receitas e despesas
    ├── relatorio.html   # Relatório mensal com gráficos
    └── clusters.html    # Análise K-Means com scatter e cotovelo
```

## Rotas da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/transacoes | Lista transações (filtros: mes, ano, tipo) |
| POST | /api/transacoes | Cria uma transação |
| PUT | /api/transacoes/{id} | Atualiza uma transação |
| DELETE | /api/transacoes/{id} | Remove uma transação |
| GET | /api/relatorio | Relatório mensal (params: mes, ano) |
| GET | /api/anos | Anos com dados registrados |
| GET | /api/clusters | Executa o K-Means (params: tipo, k) |

## Autores

- Gabriel Nerling
- Vinicius da Silva Gallina

## Instituição

URI — Universidade Regional Integrada do Alto Uruguai e das Missões  
Câmpus Erechim — Curso de Ciência da Computação  
2026
