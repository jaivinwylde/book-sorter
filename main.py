import csv
import time

import openai
import requests
from bs4 import BeautifulSoup

# Set up your API keys
OPENAI_API_KEY = ""

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY


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

        if book_item:
            # Extract rating
            rating_element = book_item.find("span", {"class": "minirating"})
            rating = (
                rating_element.text.strip().split("avg")[0].strip()[-4:]
                if rating_element
                else None
            )

            # Extract number of ratings
            num_ratings_element = rating_element
            num_ratings = (
                num_ratings_element.text.strip().split("—")[1].strip().split(" ")[0]
                if num_ratings_element
                else None
            )

            return rating, num_ratings
        return None, None
    except Exception as e:
        print(f"Error fetching Goodreads info for {title}: {e}")
        return None, None


def get_summary(title, author) -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"Provide a brief summary of the book '{title}' by {author} in 2-3 sentences",
                }
            ],
            max_tokens=256,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"Error generating summary for {title}: {e}")
        return ""


def process_book_list(input_file, output_file):
    with open(input_file, "r") as f:
        content = f.read()

    books = []
    for line in content.split("\n")[2:]:
        if "|" in line:
            parts = line.split("|")
            title = parts[1].strip()
            author = parts[2].strip()
            times_mentioned = parts[3].strip() or "0"
            books.append((title, author, times_mentioned))

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Title",
                "Author",
                "Times Mentioned",
                "Goodreads Score",
                "Number of Reviews",
                "Summary",
            ]
        )

        for title, author, times_mentioned in books:
            print(f"Processing: {title} by {author}")
            score, review_count = get_goodreads_info(title, author)
            summary = get_summary(title, author)
            print(f"Summary: {summary[:30]}\nScore: {score}\nReviews: {review_count}\n")

            writer.writerow(
                [title, author, times_mentioned, score, review_count, summary]
            )
            time.sleep(0.5)

    print(f"CSV file '{output_file}' has been created successfully.")


if __name__ == "__main__":
    input_file = "input.txt"
    output_file = "organized_book_list.csv"
    process_book_list(input_file, output_file)
