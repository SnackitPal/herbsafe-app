import xml.etree.ElementTree as ET
from Bio import Entrez

def fetch_pubmed_summary(ingredient_name):
    """
    Fetches a summary of the top PubMed article linking an ingredient to liver injury.

    Args:
        ingredient_name (str): The name of the herbal ingredient to search for.

    Returns:
        dict: A dictionary containing the 'title', 'snippet', and 'url' of the
              top article, or None if no relevant article is found or an error occurs.
    """
    Entrez.email = "herbsafe.demo@example.com"  # Required by NCBI

    try:
        # Construct the search query
        search_term = f'"{ingredient_name}" AND (hepatotoxicity OR "liver injury" OR "drug-induced liver injury")'

        # Search PubMed to get article IDs
        handle = Entrez.esearch(db="pubmed", term=search_term, retmax="1")
        record = Entrez.read(handle)
        handle.close()

        id_list = record["IdList"]
        if not id_list:
            return None  # No results found

        pmid = id_list[0]

        # Fetch the article details using the ID
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="xml")
        xml_data = handle.read()
        handle.close()

        # Parse the XML to extract details
        root = ET.fromstring(xml_data)
        article = root.find(".//PubmedArticle")

        if article is not None:
            title_element = article.find(".//ArticleTitle")
            title = title_element.text if title_element is not None else "No title found."

            abstract_element = article.find(".//AbstractText")
            snippet = "No abstract available."
            if abstract_element is not None and abstract_element.text:
                snippet = abstract_element.text[:300] + "..." if len(abstract_element.text) > 300 else abstract_element.text

            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            return {"title": title, "snippet": snippet, "url": url}

        return None

    except Exception as e:
        print(f"An error occurred while fetching from PubMed: {e}")
        return None
