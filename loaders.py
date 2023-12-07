from langchain.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchain.document_loaders.excel import UnstructuredExcelLoader
from langchain.document_loaders.epub import UnstructuredEPubLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders.text import TextLoader
from langchain.document_loaders.pdf import PyPDFLoader
from langchain.schema.document import Document

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", r"(?<=\.)", " ", ""],
)


async def remove_newlines(s):
    s = s.replace("\n", " ")
    s = s.replace("\\n", " ")
    s = s.replace("  ", " ")
    s = s.replace("  ", " ")
    return s


async def load_document(file_name, user_id):
    file_path = "downloads/" + file_name
    if file_name.endswith(".pdf"):
        docs = PyPDFLoader(file_path).load()
    elif file_name.endswith(".docx"):
        docs = UnstructuredWordDocumentLoader(file_path).load()
    elif file_name.endswith(".xlsx"):
        docs = UnstructuredExcelLoader(file_path).load()
    elif file_name.endswith(".pptx"):
        docs = UnstructuredPowerPointLoader(file_path).load()
    elif file_name.endswith(".txt"):
        docs = TextLoader(file_path).load()
    elif file_name.endswith(".csv"):
        docs = CSVLoader(file_path).load()
    elif file_name.endswith(".epub"):
        docs = UnstructuredEPubLoader(file_path).load()
    else:
        raise ValueError(f"""unsupported file format: {file_name}\n-\n-\n-\n-\nsupported file formats:

PDF [*.pdf*]
Microsoft Word [*.docx*]
Microsoft Excel [*.xlsx*]
Microsoft PowerPoint [*.pptx*]
Text [*.txt*]
CSV [*.csv*]
EPUB [*.epub*]""")

    if file_name.endswith((".xlsx", ".csv")):
        return docs
    else:
        file_contents = set()
        for doc in docs:
            page_content = await remove_newlines(doc.page_content.strip())
            file_contents.add(page_content)
        document = Document(page_content=" ".join(file_contents), metadata={"user_id": user_id})
        return text_splitter.split_documents([document])
