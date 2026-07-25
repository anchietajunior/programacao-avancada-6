# Importa o FastAPI, a injeção de dependências (Depends) e a exceção de erros HTTP
from fastapi import Depends, FastAPI, HTTPException
# Base dos schemas, a sessão de banco e o construtor de consultas
from sqlmodel import Session, SQLModel, select

# Modelos (tabelas) e infraestrutura de conexão definidos nos outros módulos
import models
from database import engine, get_session

# Cria no banco as tabelas dos modelos registrados que ainda não existem
SQLModel.metadata.create_all(engine)

# Cria a instância da aplicação, que registra as rotas e atende as requisições
app = FastAPI()


# Schema de entrada: o corpo aceito ao criar/atualizar um livro
class BookCreate(SQLModel):
    title: str
    pages: int


# Schema de saída do livro, montado a partir do objeto do ORM
class BookRead(SQLModel):
    id: int
    title: str
    pages: int
    user_id: int


# Schema de entrada do cadastro de usuário
class UserCreate(SQLModel):
    name: str
    email: str
    password: str


# Schema de saída do usuário — sem a senha, que nunca volta na resposta
class UserRead(SQLModel):
    id: int
    name: str
    email: str


# Rota GET /health, usada para verificar se a API está no ar
@app.get("/health")
def read_health():
    # Devolve um dicionário, que o FastAPI converte automaticamente em JSON
    return {"status": "Ok"}


# Cria um livro para o usuário da URL; rota aninhada expressa a relação 1:N
@app.post("/users/{user_id}/books", response_model=BookRead, status_code=201)
def create_book(user_id: int, book: BookCreate, session: Session = Depends(get_session)):
    # Garante que o dono existe antes de criar o livro
    user = session.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Monta o livro já ligado ao usuário pela chave estrangeira
    new_book = models.Book(title=book.title, pages=book.pages, user_id=user_id)
    # add coloca na sessão, commit grava no banco, refresh traz o id gerado
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book


# Lista os livros de um usuário usando a relação user.books do ORM
@app.get("/users/{user_id}/books", response_model=list[BookRead])
def list_books(user_id: int, session: Session = Depends(get_session)):
    # Garante que o usuário existe antes de listar
    user = session.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # A relação carrega os livros do usuário sem SQL escrito à mão
    return user.books


# Busca um livro pelo id; session.get procura pela chave primária
@app.get("/books/{book_id}", response_model=BookRead)
def read_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(models.Book, book_id)
    # Não achou: responde 404 em vez de devolver vazio
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# Atualiza um livro existente; PUT substitui a representação inteira
@app.put("/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, book: BookCreate, session: Session = Depends(get_session)):
    # Busca o livro no banco; 404 se não existir
    stored_book = session.get(models.Book, book_id)
    if stored_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    # Altera os campos do objeto e o commit persiste a mudança
    stored_book.title = book.title
    stored_book.pages = book.pages
    session.commit()
    session.refresh(stored_book)
    return stored_book


# Remove um livro; 204 = sucesso sem corpo na resposta
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    # Busca o livro no banco; 404 se não existir
    book = session.get(models.Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    # delete marca para remoção e o commit apaga do banco
    session.delete(book)
    session.commit()


# Cadastra um usuário no banco; Depends(get_session) injeta a sessão na rota
@app.post("/signup", response_model=UserRead, status_code=201)
def signup(user: UserCreate, session: Session = Depends(get_session)):
    # Monta a consulta e executa: existe alguém com este email?
    statement = select(models.User).where(models.User.email == user.email)
    existing_user = session.exec(statement).first()
    # 409 = conflito: o email já está em uso
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    # Senha guardada em texto puro de propósito — o hash chega
    # na aula de autenticação (ADR-0001)
    new_user = models.User(name=user.name, email=user.email, password=user.password)
    # add coloca na sessão, commit grava no banco, refresh traz o id gerado
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
