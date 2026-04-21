# Sistema de Gestão Financeira com K-Means

Sistema web de gestão financeira empresarial com aplicação do algoritmo K-Means para segmentação e análise de dados financeiros.

Projeto Integrador III — Curso de Ciência da Computação  
Universidade Regional Integrada do Alto Uruguai e das Missões — URI Erechim

---

## Sobre o projeto

O sistema permite o cadastro e controle de receitas e despesas de uma organização, aplicando o algoritmo de agrupamento K-Means para identificar padrões nos dados financeiros e auxiliar na tomada de decisões estratégicas.

## Funcionalidades

- Autenticação de usuários (login e logout)
- Cadastro, edição e exclusão de transações financeiras
- Categorização de receitas e despesas
- Aplicação do algoritmo K-Means para segmentação dos dados
- Visualização dos clusters gerados com gráficos interativos (Plotly)
- Dashboard com indicadores financeiros
- Relatórios de evolução financeira por período

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + Django |
| Banco de dados | MySQL (XAMPP) |
| Análise de dados | Pandas + Scikit-learn |
| Visualização | Plotly |
| Frontend | HTML + CSS + JavaScript |
| Controle de versão | Git + GitHub |

## Pré-requisitos

- Python 3.10+
- XAMPP com MySQL ativo
- Git

## Como rodar o projeto

**1. Clone o repositório**
```bash
git clone git@github.com:seu-usuario/sistema-gestao-financeira.git
cd sistema-gestao-financeira
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

**4. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
```
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DB_NAME=gestao_financeira
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

**5. Crie o banco de dados**

Com o XAMPP iniciado, acesse o phpMyAdmin e crie um banco chamado `gestao_financeira`.

**6. Execute as migrations**
```bash
python manage.py migrate
```

**7. Inicie o servidor**
```bash
python manage.py runserver
```

Acesse em: [http://localhost:8000](http://localhost:8000)

## Estrutura do projeto

```
sistema-gestao-financeira/
├── config/             # Configurações do Django
├── core/               # Autenticação e dashboard
├── transacoes/         # CRUD de receitas e despesas
├── analise/            # Lógica do K-Means
├── relatorios/         # Geração de gráficos com Plotly
├── static/             # CSS e JavaScript
├── templates/          # Templates HTML base
├── requirements.txt
├── manage.py
└── .env                # Não versionado
```

## Autores

- Gabriel Nerling
- Vinicius da Silva Gallina

## Instituição

URI — Universidade Regional Integrada do Alto Uruguai e das Missões  
Câmpus Erechim — Curso de Ciência da Computação  
2026
