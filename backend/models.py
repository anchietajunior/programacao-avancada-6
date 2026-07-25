from datetime import datetime

# Field configura colunas, Relationship liga as tabelas, SQLModel é a classe-mãe
from sqlmodel import Field, Relationship, SQLModel


# Modelo User: table=True transforma a classe na tabela "user" do banco
class User(SQLModel, table=True):
    # Chave primária: nasce None e o banco preenche no INSERT
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    # unique=True: o banco recusa dois usuários com o mesmo email
    email: str = Field(max_length=255, unique=True)
    password: str = Field(max_length=255)
    # Preenchido na criação do objeto, com a data/hora daquele momento
    created_at: datetime = Field(default_factory=datetime.now)

    # Lado 1 da relação 1:N — user.books lista os livros do usuário
    books: list["Book"] = Relationship(back_populates="user")


# Modelo Book: a tabela "book", o lado N da relação com User
class Book(SQLModel, table=True):
    # Chave primária: nasce None e o banco preenche no INSERT
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    pages: int
    # Chave estrangeira: cada livro pertence a um usuário
    user_id: int = Field(foreign_key="user.id")
    # Preenchido na criação do objeto, com a data/hora daquele momento
    created_at: datetime = Field(default_factory=datetime.now)

    # Lado N da relação — book.user devolve o dono do livro
    user: User | None = Relationship(back_populates="books")
