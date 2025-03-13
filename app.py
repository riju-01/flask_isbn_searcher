from flask import Flask, request, jsonify, render_template
import requests
import re

app = Flask(__name__, static_folder="static", template_folder="templates")

def clean_isbn(isbn):
    """Remove hyphens and spaces from ISBN."""
    return re.sub(r'[-\s]', '', isbn)

def convert_isbn(isbn):
    """Convert ISBN-10 to ISBN-13 and vice versa if needed."""
    isbn = clean_isbn(isbn)
    if len(isbn) == 10:  # Convert ISBN-10 to ISBN-13
        prefix = "978" + isbn[:-1]
        check_digit = (10 - (sum(int(d) * w for d, w in zip(prefix, [1, 3] * 6)) % 10)) % 10
        return prefix + str(check_digit)
    elif len(isbn) == 13 and isbn.startswith("978"):  # Convert ISBN-13 to ISBN-10
        core = isbn[3:-1]
        check_digit = (11 - (sum(int(d) * w for d, w in zip(core, [1, 3] * 5)) % 11)) % 11
        return core + ("X" if check_digit == 10 else str(check_digit))
    return isbn

def fetch_openlibrary(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    response = requests.get(url)
    data = response.json()
    book_key = f"ISBN:{isbn}"
    
    if book_key in data:
        book = data[book_key]
        return {
            "title": book.get("title", "N/A"),
            "authors": [author["name"] for author in book.get("authors", [])],
            "publishers": [publisher["name"] for publisher in book.get("publishers", [])] or ["N/A"],  # Ensure list format
            "publish_date": book.get("publish_date", "N/A"),
            "edition": book.get("edition_name", "N/A"),  # Fetch edition info
            "cover_image": book.get("cover", {}).get("large", "N/A")
        }
    return None

def fetch_googlebooks(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    data = response.json()
    
    if "items" in data:
        book = data["items"][0]["volumeInfo"]
        return {
            "title": book.get("title", "N/A"),
            "authors": book.get("authors", ["N/A"]),
            "publishers": [book.get("publisher")] if book.get("publisher") else ["Unknown Publisher"],  # Fix: Ensure list format
            "publish_date": book.get("publishedDate", "N/A"),
            "edition": book.get("contentVersion", book.get("subtitle", "N/A")),  
            "cover_image": book.get("imageLinks", {}).get("thumbnail", "N/A")
        }
    return None


def get_book_details(isbn):
    isbn = clean_isbn(isbn)  # Clean ISBN first
    isbn_10 = convert_isbn(isbn) if len(isbn) == 13 else isbn
    isbn_13 = convert_isbn(isbn) if len(isbn) == 10 else isbn
    
    details = (fetch_openlibrary(isbn) or fetch_openlibrary(isbn_10) or fetch_openlibrary(isbn_13) or
               fetch_googlebooks(isbn) or fetch_googlebooks(isbn_10) or fetch_googlebooks(isbn_13))
    
    return details if details else {"error": "Book not found in any database."}

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/get_book', methods=['POST'])
def get_book():
    isbn = request.json.get("isbn")
    book_details = get_book_details(isbn)
    return jsonify(book_details)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
