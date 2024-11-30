import requests
from bs4 import BeautifulSoup
import os
import time

# Base URL for the documentation
BASE_URL = "https://www.myquant.cn/docs2/sdk/python/API介绍/基本函数.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Directory to save the documents
SAVE_DIR = "myquant_docs"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def fetch_html(url):
    """Fetch HTML content of a URL."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        response.encoding = "utf-8"  # Automatically detect correct encoding
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_all_links(base_url):
    """Extract all links to documentation pages from the base URL."""
    html_content = fetch_html(base_url)
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, "html.parser")
    links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        # Making sure the link is internal and relevant
        if href.startswith("/docs2/sdk/python"):
            full_url = "https://www.myquant.cn" + href
            links.append(full_url)
    return list(set(links))  # Remove duplicates

def save_document(url, content):
    """Save the document content to a local file as a text file."""
    filename = url.split("/")[-1] + ".txt"
    file_path = os.path.join(SAVE_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        try:
            file.write(content)
        except UnicodeEncodeError:
            print(f"Error saving {url}: Unable to encode content")

def crawl_myquant_docs():
    """Main function to crawl and save all documentation pages."""
    links = get_all_links(BASE_URL)
    print(f"Found {len(links)} links to documentation pages.")

    for index, link in enumerate(links):
        print(f"[{index + 1}/{len(links)}] Fetching {link}")
        doc_content = fetch_html(link)
        if doc_content:
            save_document(link, doc_content)
        time.sleep(1)  # Be polite and avoid overwhelming the server

if __name__ == "__main__":
    crawl_myquant_docs()
