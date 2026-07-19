# Importa o FastAPI e a exceção usada para responder erros HTTP
from fastapi import FastAPI, HTTPException

# Cria a instância da aplicação, que registra as rotas e atende as requisições
app = FastAPI()

# "Banco de dados" em memória desta aula: uma lista simples de livros
books = [
    {"id": 1, "name": "Dom Casmurro"},
    {"id": 2, "name": "O Hobbit"},
    {"id": 3, "name": "Clean Code"},
]


# Rota GET /health, usada para verificar se a API está no ar
@app.get("/health")
def read_health():
    # Devolve um dicionário, que o FastAPI converte automaticamente em JSON
    return {"status": "Ok"}


# Lista os livros; o parâmetro de query "name" filtra pelo nome
@app.get("/api/books")
def list_books(name: str = ""):
    # Sem filtro, devolve a lista completa
    if name == "":
        return books
    # Com filtro, devolve só os livros cujo nome contém o termo (ignorando maiúsculas)
    return [book for book in books if name.lower() in book["name"].lower()]


# Busca um livro pelo id vindo do path da URL
@app.get("/api/books/{book_id}")
def read_book(book_id: int):
    # Percorre a lista procurando o livro com o id pedido
    for book in books:
        if book["id"] == book_id:
            return book
    # Não achou: responde 404 em vez de devolver vazio
    raise HTTPException(status_code=404, detail="Book not found")


# Cria um livro a partir do corpo JSON da requisição; 201 = criado
@app.post("/api/books", status_code=201)
def create_book(book: dict):
    # Gera o próximo id a partir do tamanho da lista e monta o novo livro
    new_book = {"id": len(books) + 1, "name": book["name"]}
    # Guarda na lista em memória e devolve o livro criado
    books.append(new_book)
    return new_book
