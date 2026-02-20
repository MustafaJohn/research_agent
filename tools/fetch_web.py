# Code for fetching data from the web
import os
import time
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS  
import hashlib
import re
import fitz


class FetchWebTool:
    """
    A tool for fetching data from the web using DuckDuckGo search and BeautifulSoup.
    Responsibilities:
      - Search the web for a query
      - Download raw HTML
      - Extract readable text
      - Store raw pages to disk
    """

    def __init__(self, raw_data_dir="data\\raw", rate_limit=1.5):
        self.raw_data_dir = raw_data_dir
        self.rate_limit = rate_limit
        os.makedirs(self.raw_data_dir, exist_ok=True)

    # Function to search on DuckDuckGo
    def search(self, query, n_results=10):
        """Returns a list of URLs from DuckDuckGo search results."""
        with DDGS() as ddgs:
            results = ddgs.text(query, region="uk-en", max_results=n_results)
            urls = [result["href"] for result in results if "href" in result]
        return urls 
    
    # Function to clean the URL
    

    def _clean_url(self, url: str) -> str:

        h = hashlib.md5(url.encode()).hexdigest()[:12]
        base = re.sub(r"[^a-zA-Z0-9_-]", "_", url)
        return f"{base[:50]}_{h}.txt"

    def _already_downloaded(self, url):
        """Check if this URL has already been fetched."""
        filename = self._clean_url(url)
        return os.path.exists(os.path.join(self.raw_data_dir, filename))
    
    def fetch_url(self, url):

        filename = self._clean_url(url)
        file_path = os.path.join(self.raw_data_dir, filename)

        if self._already_downloaded(url):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        try:
            response = requests.get(
                url,
                timeout=12,
                headers={"User-Agent": "Research Agent"}
            )
            response.raise_for_status()

        except Exception as e:
            print(f"[ERROR fetch] {url} -> {e}")
            return ""

        text = ""

        ctype = response.headers.get("Content-Type", "").lower()

        if "text/html" in ctype:
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script","style","header","footer","nav"]):
                tag.extract()

            text = soup.get_text(separator="\n")

        elif "application/pdf" in ctype:
            text = self.parse_pdf(response.content)

        else:
            print(f"[SKIP unsupported type] {ctype} -> {url}")
            return ""

        # Safety guard
        if not text:
            return ""

        cleaned = "\n".join(
            line.strip()
            for line in text.splitlines()
            if line.strip()
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        time.sleep(self.rate_limit)
        return cleaned


    def fetch_query(self, query, n_results=10):
        """ Search + fetch URLs for a given input"""
        urls = self.search(query, n_results=n_results)
        pages = []
        print("\nSources fetched:")
        # Presenting a high level output of urls and their text  
        for url in urls:
            text = self.fetch_url(url)
            if text:
                print(f"- {url}")
            pages.append({'url': url, 'text': text})
        
        return pages

    def parse_pdf(self,content_bytes):

        text = ""

        try:
            with fitz.open(stream=content_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()

        except Exception as e:
            print("[PDF PARSE FAIL]", e)

        return text


#if __name__ == "__main__":
#    tool = FetchWebTool()
#    data = tool.fetch_query("potato", n_results=2)
#    print(f"Fetched {len(data)} pages.") 