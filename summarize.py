from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize, word_tokenize
from bs4 import BeautifulSoup
import networkx as nx
import requests
import nltk

nltk.download('punkt')


def preprocess_text(text):
    sentences = sent_tokenize(text)
    processed_sentences = []
    for sentence in sentences:
        words = word_tokenize(sentence)
        filtered_words = [word for word in words if word.isalnum()]
        processed_sentences.append(" ".join(filtered_words))
    return sentences, processed_sentences


def build_similarity_matrix(processed_sentences):
    vectorizer = TfidfVectorizer().fit_transform(processed_sentences)
    vectors = vectorizer.toarray()
    similarity_matrix = cosine_similarity(vectors)
    return similarity_matrix


def summarize(query: str, url: str, num_sentences: int = 5) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    keywords = word_tokenize(query.lower())
    text = ""
    for p in soup.find_all("p"):
        lowered_text = p.text.lower()
        if any(keyword in lowered_text for keyword in keywords):
            text += p.text + "\n"
    sentences, processed_sentences = preprocess_text(text)
    similarity_matrix = build_similarity_matrix(processed_sentences)
    nx_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(nx_graph)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    summary = " ".join([sentence for score, sentence in ranked_sentences[:num_sentences]])
    return summary
