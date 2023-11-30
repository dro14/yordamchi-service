from langchain.document_loaders.word_document import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders.text import TextLoader
from langchain.document_loaders.pdf import PyPDFLoader
from langchain.schema.document import Document

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", r"(?<=\.)", " ", ""],
)


def remove_newlines(s):
    s = s.replace("\n", " ")
    s = s.replace("\\n", " ")
    s = s.replace("  ", " ")
    s = s.replace("  ", " ")
    return s


def load_document(file_name, user_id):
    file_path = "downloads/" + file_name
    if file_path.endswith(".pdf"):
        pages = PyPDFLoader(file_path, extract_images=True).load()
    elif file_path.endswith((".doc", ".docx")):
        pages = Docx2txtLoader(file_path).load()
    elif file_path.endswith(".txt"):
        pages = TextLoader(file_path).load()
    else:
        raise ValueError(f"Unsupported file format: {file_name}")

    file_contents = set()
    for page in pages:
        file_contents.add(remove_newlines(page.page_content.strip()))
    document = Document(page_content=" ".join(file_contents), metadata={"user_id": user_id})
    return text_splitter.split_documents([document])
