import os
import requests
from langchain_core.tools import tool

@tool
def search_pubmed(query: str, max_results: int = 3) -> str:
    """Searches PubMed for a given query and returns formatted abstracts. Use this to find peer-reviewed literature dynamically."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    try:
        search_resp = requests.get(base_url, params={
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results
        })
        search_resp.raise_for_status()
        id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return "No results found."

        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_resp = requests.get(summary_url, params={
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json"
        })
        summary_resp.raise_for_status()
        result = summary_resp.json().get("result", {})
        
        output = []
        for uid in id_list:
            item = result.get(uid, {})
            title = item.get("title", "No Title")
            source = item.get("source", "Unknown Source")
            output.append(f"Title: {title}\nJournal: {source}\nPMID: {uid}")
        
        return "\n\n".join(output)
    except Exception as e:
        return f"Error querying PubMed: {e}"

@tool
def check_schema_org(entity: str) -> str:
    """Checks if a given term exists natively in the Schema.org vocabulary. Pass abstract nouns like 'Dataset' or 'manufacturer'"""
    try:
        resp = requests.get(f"https://schema.org/{entity}")
        if resp.status_code == 200:
            return f"Entity '{entity}' exists in schema.org. It is structurally valid."
        else:
            return f"Entity '{entity}' NOT found natively in schema.org. Custom mapping required."
    except Exception as e:
        return f"Error contacting schema.org: {e}"

@tool
def write_manuscript_section(section_name: str, content: str) -> str:
    """Writes a drafted section to the disk in the 'Drafts' directory for persistent IO."""
    drafts_dir = os.path.join(os.path.dirname(__file__), "..", "Drafts")
    os.makedirs(drafts_dir, exist_ok=True)
    filename = f"{section_name.lower().replace(' ', '_')}.md"
    filepath = os.path.join(drafts_dir, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"SUCCESS: Wrote '{section_name}' to {filepath}"
    except Exception as e:
        return f"FAILED to write file: {e}"

@tool
def search_you_engine(query: str) -> str:
    """Searches the live web using the You.com API. Use this to find current news, web pages, or broad research that requires live web context outside of PubMed."""
    api_key = os.getenv("YOU_API_KEY")
    if not api_key:
        return "ERROR: 'YOU_API_KEY' is not set in the environment variables."
        
    url = "https://api.ydc-index.io/v1/search"
    headers = {"X-API-Key": api_key, "Accept": "application/json"}
    params = {"query": query}
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        snippets = []
        hits = data.get("hits", [])
        if not hits:
            return "No web results found on You.com."
            
        for count, hit in enumerate(hits[:5]):
            title = hit.get("title", "No Title")
            link = hit.get("url", "No URL")
            description = "\n".join(hit.get("snippets", []))
            if not description:
                 description = hit.get("description", "No Snippet")
            snippets.append(f"{count+1}. Title: {title}\nURL: {link}\nSnippet: {description}")
            
        return "\n\n".join(snippets)
    except Exception as e:
        return f"Error contacting You.com API: {e}"
