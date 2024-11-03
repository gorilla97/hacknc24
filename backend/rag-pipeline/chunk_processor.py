import re
from typing import List, Dict
from transformers import BertTokenizerFast as Tokenizer
from tqdm.auto import tqdm

class ChunkMetadata:
    def __init__(self, pre_context: str, text: str, post_context: str, source_url: str, source_description: str, order: int):
        self.pre_context = pre_context
        self.text = text
        self.post_context = post_context
        self.source_url = source_url
        self.source_description = source_description
        self.order = order

    def to_dict(self) -> Dict:
        return {
            "pre_context": self.pre_context,
            "text": self.text,
            "post_context": self.post_context,
            "source_url": self.source_url,
            "source_description": self.source_description,
            "order": self.order
        }

def chunk_text(text: str, chunk_size: int = 5000) -> List[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

def clean_tokens(tokens):
    words = []
    for token in tokens:
        if token.startswith("##") and words:
            words[-1] = words[-1] + token[2:]
        else:
            words.append(token)
    return " ".join(words)

def get_semantic_chunks(text: str, chunk_size: int = 200) -> List[str]:
    tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
    tokens = tokenizer.tokenize(text)
    chunks = [" ".join(tokens[i : i + chunk_size]) for i in range(0, len(tokens), chunk_size)]
    
    cleaned_chunks = [clean_tokens(chunk.split()) for chunk in chunks]
    print(f"Text split into {len(cleaned_chunks)} semantic chunks")
    return cleaned_chunks

def create_chunk_objects(semantic_chunks: List[str], source_url: str, source_description: str) -> List[ChunkMetadata]:
    chunk_objects = []
    for i, chunk in enumerate(semantic_chunks):
        before = semantic_chunks[i - 1] if i > 0 else ""
        after = semantic_chunks[i + 1] if i < len(semantic_chunks) - 1 else ""
        chunk_objects.append(
            ChunkMetadata(
                pre_context=before,
                text=chunk,
                post_context=after,
                source_url=source_url,
                source_description=source_description,
                order=i,
            )
        )
    return chunk_objects

def split_list(input_list: List[str], slice_size: int) -> List[List[str]]:
    return [input_list[i:i + slice_size] for i in range(0, len(input_list), slice_size)]

def chunk_sentences(pdf_text: List[Dict], chunk_size: int = 5) -> List[Dict]:
    for item in tqdm(pdf_text, desc="Splitting sentences into chunks"):
        item["sentence_chunks"] = split_list(input_list=item["sentences"], slice_size=chunk_size)
        item["num_chunks"] = len(item["sentence_chunks"])
    return pdf_text

def chunk_pager(pages_and_texts: List[Dict]) -> List[Dict]:
    pages_and_chunks = []
    
    for item in tqdm(pages_and_texts, desc="Processing pages into chunks"):
        for sentence_chunk in item["sentence_chunks"]:
            chunk_dict = {
                "page_number": item["page_num"],
                "sentence_chunk": " ".join(sentence_chunk).replace("  ", " ").strip()
            }
            
            chunk_dict["chunk_char_count"] = len(chunk_dict["sentence_chunk"])
            chunk_dict["chunk_word_count"] = len(chunk_dict["sentence_chunk"].split())
            chunk_dict["chunk_token_count"] = len(chunk_dict["sentence_chunk"]) / 4

            pages_and_chunks.append(chunk_dict)

    return pages_and_chunks

def merge_small_chunks(pages_and_chunks: List[Dict], min_word_count: int = 30) -> List[Dict]:
    merged_chunks = []
    buffer_chunk = None

    for chunk in pages_and_chunks:
        if chunk["chunk_word_count"] < min_word_count:
            if buffer_chunk:
                buffer_chunk["sentence_chunk"] += " " + chunk["sentence_chunk"]
                buffer_chunk["chunk_word_count"] += chunk["chunk_word_count"]
                buffer_chunk["chunk_char_count"] += chunk["chunk_char_count"]
                buffer_chunk["chunk_token_count"] += chunk["chunk_token_count"]
            else:
                buffer_chunk = chunk
        else:
            if buffer_chunk:
                chunk["sentence_chunk"] = buffer_chunk["sentence_chunk"] + " " + chunk["sentence_chunk"]
                chunk["chunk_word_count"] += buffer_chunk["chunk_word_count"]
                chunk["chunk_char_count"] += buffer_chunk["chunk_char_count"]
                chunk["chunk_token_count"] += buffer_chunk["chunk_token_count"]
                buffer_chunk = None
            merged_chunks.append(chunk)

    if buffer_chunk:
        merged_chunks.append(buffer_chunk)

    return merged_chunks