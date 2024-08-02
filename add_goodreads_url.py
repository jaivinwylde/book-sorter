import csv

import requests
from bs4 import BeautifulSoup


def get_goodreads_info(title, author):
    try:
        search_query = f"{title} {author}".replace(" ", "+")
        url = f"https://www.goodreads.com/search?q={search_query}"
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            },
        )
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the first book result
        book_item = soup.find("tr", {"itemtype": "http://schema.org/Book"})
        url: str = book_item.find("a", {"class": "bookTitle"}).get("href", "")
        return f"https://www.goodreads.com{url.split("?")[0]}"

    except Exception as e:
        print(f"Error fetching Goodreads info for {title}: {e}")
        return None, None


with open("books.csv", "r") as file:
    csv_reader = csv.DictReader(file)
    fieldnames = csv_reader.fieldnames
    rows = []
    if fieldnames is None:
        raise ValueError("No fieldnames found in CSV file")

    # Iterate through the rows and extract title and author
    for row in csv_reader:
        title = row["Title"]
        author = row["Author"]
        url = get_goodreads_info(title, author)
        row["Goodreads URL"] = url
        rows.append(row)

    # Now we can loop through the book_list
    with open("updated_books.csv", "w", newline="") as file:
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(rows)
