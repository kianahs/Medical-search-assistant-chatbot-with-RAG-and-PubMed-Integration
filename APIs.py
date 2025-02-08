import requests
import xml.etree.ElementTree as ET
import os


def search_pubmed(query, max_results=10):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "usehistory": "y"
    }
    response = requests.get(url, params=params)
    return response.text


def parse_results(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()
    ids = [id.text for id in root.findall(".//Id")]
    return ids


def fetch_details(pmid_list):
    ids = ",".join(pmid_list)
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ids,
        "retmode": "xml"
    }
    response = requests.get(url, params=params)
    return response.text


def parse_article_details(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()

    articles = []
    for article in root.findall(".//PubmedArticle"):
        article_info = {}

        title = article.find(".//ArticleTitle")
        article_info["title"] = title.text if title is not None else "No title"

        authors = []
        for author in article.findall(".//Author"):
            last_name = author.find(".//LastName")
            fore_name = author.find(".//ForeName")
            authors.append(
                f"{fore_name.text} {last_name.text}" if last_name is not None else "No name")
        article_info["authors"] = authors

        source = article.find(".//Source")
        article_info["journal"] = source.text if source is not None else "No journal"

        pub_date = article.find(".//PubDate")
        date = pub_date.find(".//Year") if pub_date is not None else None
        article_info["publication_year"] = date.text if date is not None else "No date"

        abstract_texts = article.findall(".//AbstractText")
        if abstract_texts:
            article_info["abstract"] = " ".join(
                [abs_text.text for abs_text in abstract_texts if abs_text.text])
        else:
            article_info["abstract"] = "No abstract"

        articles.append(article_info)

    return articles


def get_pub_med_articles(category='health', num=100):
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:10809"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"

    # Search PubMed
    search_results = search_pubmed(category, num)

    # Parse the list of PMIDs
    pmids = parse_results(search_results)

    #  Fetch article details
    article_details = fetch_details(pmids)

    # Parse the article details (schema)
    articles = parse_article_details(article_details)

    # print(articles[0])

    return articles
