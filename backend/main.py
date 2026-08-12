# Importa o FastAPI, a exceção de erros HTTP e a base dos schemas Pydantic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Cria a instância da aplicação, que registra as rotas e atende as requisições
app = FastAPI()


# Modelo do recurso Book: Python puro, sem nada de FastAPI
class Book:
    # Único portão de entrada: não existe Book sem id e sem name
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    # Como o objeto se apresenta no terminal, útil ao depurar
    def __repr__(self):
        return f"Book(id={self.id}, name={self.name!r})"


# Schema de entrada: o corpo aceito ao criar ou atualizar um livro (só o nome)
class BookCreate(BaseModel):
    name: str


# "Banco de dados" em memória desta aula: uma lista de objetos Book
books = [
    Book(id=1, name="Dom Casmurro"),
    Book(id=2, name="O Hobbit"),
    Book(id=3, name="Clean Code"),
]


# Calcula o próximo id a partir do último livro da lista
def next_book_id():
    # Lista vazia não tem último livro: a numeração começa em 1
    if not books:
        return 1
    # Com livros na lista, o próximo id é um a mais que o do último
    return books[-1].id + 1


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
    return [book for book in books if name.lower() in book.name.lower()]


# Busca um livro pelo id vindo do path da URL
@app.get("/api/books/{book_id}")
def read_book(book_id: int):
    # Percorre a lista procurando o livro com o id pedido
    for book in books:
        # Acesso por atributo: é o objeto respondendo, não uma chave de dicionário
        if book.id == book_id:
            return book
    # Não achou: responde 404 em vez de devolver vazio
    raise HTTPException(status_code=404, detail="Book not found")


# Cria um livro; o corpo é validado pelo schema BookCreate antes de chegar aqui
@app.post("/api/books", status_code=201)
def create_book(book: BookCreate):
    # Entra BookCreate, sai Book: o dado do cliente vira objeto nosso aqui
    new_book = Book(id=next_book_id(), name=book.name)
    # Guarda na lista em memória e devolve o livro criado
    books.append(new_book)
    return new_book


# Atualiza um livro existente; PUT substitui a representação inteira
@app.put("/api/books/{book_id}")
def update_book(book_id: int, book: BookCreate):
    # Procura o livro pedido na lista
    for stored_book in books:
        if stored_book.id == book_id:
            # O objeto é mutável: trocamos o atributo, sem recriar nada
            stored_book.name = book.name
            return stored_book
    # Não achou: responde 404, igual ao GET por id
    raise HTTPException(status_code=404, detail="Book not found")


# Remove um livro; 204 = deu certo e não há corpo para devolver
@app.delete("/api/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    # Procura o livro pedido na lista
    for book in books:
        if book.id == book_id:
            books.remove(book)
            # return sem valor: o 204 proíbe corpo na resposta
            return
    # Não achou: responde 404
    raise HTTPException(status_code=404, detail="Book not found")
