from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()

# Configuração dos diretórios
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = "db.sqlite3"

# Criação do banco de dados e dados de exemplo
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS contas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        cnpj TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conta_id INTEGER,
        nome TEXT,
        classificacao FLOAT,
        imagem_url TEXT,
        FOREIGN KEY(conta_id) REFERENCES contas(id)
    )
    """)

    # Insere dados de exemplo se estiver vazio
    cur.execute("SELECT COUNT(*) FROM contas")
    if cur.fetchone()[0] == 0:
        contas = [
            ("Tramontina", "12.345.678/0001-00"),
            ("Sicredi", "98.765.432/0001-11"),
            ("Stefanini", "11.222.333/0001-55")
        ]
        cur.executemany("INSERT INTO contas (nome, cnpj) VALUES (?, ?)", contas)

        produtos = [
            (1, "Conjunto de Panelas", 0.95, "https://picsum.photos/200?1"),
            (1, "Faqueiro Inox", 0.88, "https://picsum.photos/200?2"),
            (1, "Tábua de Corte", 0.67, "https://picsum.photos/200?3"),
            (2, "Conta Corrente Premium", 0.93, "https://picsum.photos/200?4"),
            (2, "Cartão Black", 0.89, "https://picsum.photos/200?5"),
            (3, "Serviço de Consultoria", 0.92, "https://picsum.photos/200?6"),
            (3, "Desenvolvimento BI", 0.87, "https://picsum.photos/200?7")
        ]
        cur.executemany("""
            INSERT INTO produtos (conta_id, nome, classificacao, imagem_url)
            VALUES (?, ?, ?, ?)
        """, produtos)

    conn.commit()
    conn.close()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, nome, cnpj FROM contas")
    contas = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "contas": contas})


@app.post("/produtos", response_class=HTMLResponse)
def produtos(request: Request, conta_id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT nome FROM contas WHERE id = ?", (conta_id,))
    conta_nome = cur.fetchone()[0]

    cur.execute("""
        SELECT nome, 
               classificacao,
               product_code, 
               imagem_url
        FROM produtos
        WHERE conta_id = ?
        ORDER BY classificacao DESC
    """, (conta_id,))
    produtos = cur.fetchall()
    conn.close()

    return templates.TemplateResponse("produtos.html", {
        "request": request,
        "conta_nome": conta_nome,
        "produtos": produtos
    })


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        init_db()

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
