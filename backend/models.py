from datetime import datetime

# Tipos e funções do SQLAlchemy usados para definir colunas e relações
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# Modelo User: cada atributo Mapped vira uma coluna da tabela "user"
class User(Base):
    __tablename__ = "user"

    # Chave primária, gerada pelo próprio banco
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    # unique=True: o banco recusa dois usuários com o mesmo email
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    # O próprio banco preenche com a data/hora do INSERT
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Lado 1 da relação 1:N — user.books lista os livros do usuário
    books: Mapped[list["Book"]] = relationship(back_populates="user")


# Modelo Book: a tabela "book", o lado N da relação com User
class Book(Base):
    __tablename__ = "book"

    # Chave primária, gerada pelo próprio banco
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    pages: Mapped[int]
    # Chave estrangeira: cada livro pertence a um usuário
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    # O próprio banco preenche com a data/hora do INSERT
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Lado N da relação — book.user devolve o dono do livro
    user: Mapped["User"] = relationship(back_populates="books")
