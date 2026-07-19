# Importa o FastAPI, a exceção de erros HTTP e a base dos schemas Pydantic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Cria a instância da aplicação, que registra as rotas e atende as requisições
app = FastAPI()


# Schema de entrada: o corpo aceito ao criar/atualizar um livro (só o nome)
class BookCreate(BaseModel):
    name: str


# Schema de saída: o formato do livro devolvido pela API (com id)
class Book(BaseModel):
    id: int
    name: str


# "Banco de dados" em memória desta aula: uma lista simples de livros
books = [
    {"id": 1, "name": "Dom Casmurro"},
    {"id": 2, "name": "O Hobbit"},
    {"id": 3, "name": "Clean Code"},
]
# Contador do próximo id, para não depender do tamanho da lista
next_book_id = 4


# Rota GET /health, usada para verificar se a API está no ar
@app.get("/health")
def read_health():
    # Devolve um dicionário, que o FastAPI converte automaticamente em JSON
    return {"status": "Ok"}


# Lista os livros; response_model valida/filtra a resposta como lista de Book
@app.get("/api/books", response_model=list[Book])
def list_books(name: str = ""):
    # Sem filtro, devolve a lista completa
    if name == "":
        return books
    # Com filtro, devolve só os livros cujo nome contém o termo (ignorando maiúsculas)
    return [book for book in books if name.lower() in book["name"].lower()]


# Busca um livro pelo id vindo do path da URL
@app.get("/api/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    # Percorre a lista procurando o livro com o id pedido
    for book in books:
        if book["id"] == book_id:
            return book
    # Não achou: responde 404 em vez de devolver vazio
    raise HTTPException(status_code=404, detail="Book not found")


# Cria um livro; o corpo é validado pelo schema BookCreate; 201 = criado
@app.post("/api/books", response_model=Book, status_code=201)
def create_book(book: BookCreate):
    # global: a função altera a variável de módulo, não uma cópia local
    global next_book_id
    # Monta o novo livro com o próximo id e avança o contador
    new_book = {"id": next_book_id, "name": book.name}
    next_book_id += 1
    # Guarda na lista em memória e devolve o livro criado
    books.append(new_book)
    return new_book


# Atualiza um livro existente; PUT substitui a representação inteira
@app.put("/api/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookCreate):
    # Procura o livro e, se existir, troca o nome pelo novo
    for stored_book in books:
        if stored_book["id"] == book_id:
            stored_book["name"] = book.name
            return stored_book
    # Não achou: responde 404
    raise HTTPException(status_code=404, detail="Book not found")


# Remove um livro; 204 = sucesso sem corpo na resposta
@app.delete("/api/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    # Procura o livro e, se existir, remove da lista
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return
    # Não achou: responde 404
    raise HTTPException(status_code=404, detail="Book not found")
