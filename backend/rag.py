import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from backend.config import Config
from backend.logger import log_info, log_error

# Paths come from Config
KNOWLEDGE_DIR = Config.KNOWLEDGE_DIR
VECTOR_STORE_PATH = Config.VECTOR_STORE_PATH

# Initialize embeddings (Sentence-Transformers)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def build_vector_store():
    """
    Loads medical knowledge from files, splits them into chunks, 
    and saves them in a FAISS vector database.
    """
    try:
        if not os.path.exists(KNOWLEDGE_DIR):
            os.makedirs(KNOWLEDGE_DIR)
            return "Knowledge directory created. Please add medical text files and try again."

        # Load all .txt files from the knowledge directory
        loader = DirectoryLoader(KNOWLEDGE_DIR, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()

        if not documents:
            return "No medical data found in the knowledge directory."

        # Split into chunks for better retrieval
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)

        # Create and save FAISS index
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(VECTOR_STORE_PATH)
        return "FAISS index rebuilt successfully."

    except Exception as e:
        return f"Error building RAG system: {str(e)}"

def retrieve_context(query: str, top_k=3):
    """
    Searches the FAISS vector database for relevant medical context based on the query.
    """
    try:
        # Load the index
        if not os.path.exists(VECTOR_STORE_PATH):
            # If index doesn't exist, try building it first
            res = build_vector_store()
            if "success" not in res.lower():
                return f"Vector store not found and build failed: {res}"

        vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        
        # Perform similarity search
        docs = vector_store.similarity_search(query, k=top_k)
        
        # Combine content from retrieved docs
        context = "\n\n".join([doc.page_content for doc in docs])
        return context

    except Exception as e:
        print(f"Error during context retrieval: {str(e)}")
        return "No relevant context found due to an error."

# Build index automatically on first import if not present
if not os.path.exists(VECTOR_STORE_PATH):
    build_vector_store()
