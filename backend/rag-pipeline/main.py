from pdf_processor import open_and_read_pdf
from sentence_splitter import complete_sentences
from chunk_processor import create_chunk_objects, get_semantic_chunks
from embedding_processor import generate_finbert_embeddings, upsert_embeddings_to_pinecone, load_finbert_model
from file_io import write_to_notepad
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="app/core/.env")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
if pinecone_api_key is None:
    raise ValueError("Pinecone API key is not set. Please check your .env file.")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def process_pdf_pipeline(pdf_path: str, output_text_path: str, source_url: str, source_description: str, chunk_size: int = 5):
    # Step 1: Read PDF and extract text
    pdf_text = open_and_read_pdf(pdf_path)

    # Step 2: Split text into sentences
    pdf_sentences = complete_sentences(pdf_text)

    # Step 3: Create sentence-based chunks from each page's sentences
    for item in pdf_sentences:
        item["text"] = " ".join(item["sentences"])  # Join sentences to form full text for each page

    # Step 4: Create semantic chunks across all pages
    full_text = " ".join([item["text"] for item in pdf_sentences])
    semantic_chunks = get_semantic_chunks(full_text)

    # Step 5: Create chunk objects with context
    chunk_objects = create_chunk_objects(semantic_chunks, source_url, source_description)

    # Load FinBERT model and tokenizer
    tokenizer, model = load_finbert_model()

    # Step 6: Generate FinBERT embeddings for each chunk
    chunk_vectors = generate_finbert_embeddings(chunk_objects, tokenizer=tokenizer, model=model)

    # Step 7: Upsert embeddings into Pinecone
    upsert_embeddings_to_pinecone(chunk_vectors, pinecone_api_key=pinecone_api_key, index_name="unchacks24", namespace="unchacks24")

    # Optional: Write processed text to a file for debugging
    all_text = "\n".join([item["text"] for item in pdf_sentences])
    write_to_notepad(all_text, output_text_path)

    print("Pipeline completed successfully.")

if __name__ == "__main__":
    pdf_path = "/Users/pranav/Downloads/test_doc.pdf"
    output_text_path = "/Users/pranav/Downloads/blank_test.pdf"
    source_url = "https://www.investors.com/news/technology/artificial-intelligence-stocks/"
    source_description = "Sample PDF document for RAG pipeline"
    process_pdf_pipeline(pdf_path, output_text_path, source_url, source_description)