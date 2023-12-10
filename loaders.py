from langchain.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchain.document_loaders.excel import UnstructuredExcelLoader
from langchain.document_loaders.epub import UnstructuredEPubLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders.text import TextLoader
from langchain.document_loaders.pdf import PyPDFLoader
from pypandoc.pandoc_download import download_pandoc
from langchain.schema.document import Document
import csv
import os

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", r"(?<=\.)", " ", ""],
)


def remove_newlines(s: str) -> str:
    s = s.replace("\n", " ")
    s = s.replace("\\n", " ")
    s = s.replace("  ", " ")
    s = s.replace("  ", " ")
    return s


def clean_csv(file_path: str) -> None:
    f = open(file_path, "r")
    rows = csv.reader(f)
    cleaned_rows = []
    for row in rows:
        add = False
        for item in row:
            if item.strip():
                add = True
        if add:
            for i in range(len(row)):
                row[i] = remove_newlines(row[i].strip())
            cleaned_rows.append(row)
    f.close()

    f = open(file_path, "w")
    writer = csv.writer(f)
    writer.writerows(cleaned_rows)
    f.close()


def load_document(file_name: str, user_id: int) -> list[Document]:
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
        clean_csv(file_path)
        docs = CSVLoader(file_path).load()
    elif file_name.endswith(".epub"):
        download_pandoc()
        docs = UnstructuredEPubLoader(file_path).load()
    else:
        os.remove(file_path)
        raise ValueError(f"""unsupported file format: {file_name}
-
-
-
-
supported file formats:

PDF *[.pdf]*
Microsoft Word *[.docx]*
Microsoft Excel *[.xlsx]*
Microsoft PowerPoint *[.pptx]*
Text *[.txt]*
CSV *[.csv]*
EPUB *[.epub]*""")

    os.remove(file_path)
    if file_name.endswith((".xlsx", ".csv")):
        return docs
    else:
        contents = set()
        for doc in docs:
            content = remove_newlines(doc.page_content.strip())
            contents.add(content)
        document = Document(page_content=" ".join(contents), metadata={"user_id": user_id})
        return text_splitter.split_documents([document])
