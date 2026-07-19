from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()


class BookCreate(BaseModel):
    title: str
    pages: int


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    pages: int
    user_id: int


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def read_health():
    return {"status": "Ok"}


@app.post("/users/{user_id}/books", response_model=BookRead, status_code=201)
def create_book(user_id: int, book: BookCreate, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    new_book = models.Book(title=book.title, pages=book.pages, user_id=user_id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@app.get("/users/{user_id}/books", response_model=list[BookRead])
def list_books(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.books


@app.get("/books/{book_id}", response_model=BookRead)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):
    stored_book = db.get(models.Book, book_id)
    if stored_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    stored_book.title = book.title
    stored_book.pages = book.pages
    db.commit()
    db.refresh(stored_book)
    return stored_book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()


@app.post("/signup", response_model=UserRead, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.scalar(select(models.User).where(models.User.email == user.email))
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    # password stored in plain text on purpose — hashing arrives
    # in the authentication lesson (ADR-0001)
    new_user = models.User(name=user.name, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
