from langchain.tools import tool
from langchain_tavily import TavilySearch
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

tavily = TavilySearch(
    max_results = 3
)

@tool
def web_search(topic : str) -> str:
    "Search the web to collect information about the given topic."
    results = []
    response = tavily.invoke({
        "query" : topic
    })

    for i in response['results']:
        results.append(f"Title : {i['title']}\nURL : {i['url']}\nSnippet : {i['content'][:200]}\n")

    return "\n".join(results)

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"