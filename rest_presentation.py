from fastapi import (
    FastAPI,
    Request,
)

app = FastAPI()


@app.get("/books")
async def get_books(request: Request):
    user_agent = request.headers.get("User-Agent", "")
    if "python-requests" in user_agent:
        return {"books": ["Book 1", "Book 2"], "format": "Python-specific"}
    return {"books": ["Book 1", "Book 2"], "format": "default"}


from fastapi import FastAPI

app = FastAPI()


@app.get("/books")
async def get_books():
    return {"books": ["Book 1", "Book 2"]}


from fastapi import FastAPI

app = FastAPI()


@app.post("/create-book")
async def create_book(book: dict):
    # Implementation here
    return {"message": "Book created"}


from fastapi import FastAPI

app = FastAPI()


@app.post("/books")
async def create_book(book: dict):
    return {"message": "Book created"}


from fastapi import FastAPI

app = FastAPI()

database_of_books = {}
next_book_id = 1


@app.post("/books")
async def create_book(book: dict):
    global next_book_id
    database_of_books[next_book_id] = book
    next_book_id += 1
    return {"message": "Book created"}


@app.get("/books/{book_id}")
async def get_book(book_id: int):
    return {"book": database_of_books.get(book_id)}


import uuid

from fastapi import FastAPI

app = FastAPI()


@app.post("/books")
async def create_book(book: dict):
    book_id = str(uuid.uuid4())
    # In a real application, book data would be stored in
    # a database with the generated book_id
    return {"message": "Book created", "book_id": book_id}


@app.get("/books/{book_id}")
async def get_book(book_id: str):
    # Fetch book data from a database or other external
    # service using the book_id
    return {"book": {"id": book_id, "title": "Example Book"}}
