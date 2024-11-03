import fitz
from tqdm.auto import tqdm
from typing import List, Dict

def text_formatter(text: str) -> str:
    return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()

def open_and_read_pdf(pdf_path: str) -> List[Dict]:
    pdf_document = fitz.open(pdf_path)
    pdf_text = []
    for page_num in tqdm(range(pdf_document.page_count), desc="Reading PDF"):
        page = pdf_document[page_num]
        text = page.get_text("text")
        text = text_formatter(text)
        pdf_text.append({
            "page_num": page_num + 1,
            "page_char_count": len(text),
            "page_word_count": len(text.split(" ")),
            "raw_page_sent_count": text.count(". "),
            "page_tokens": len(text) / 4,  # Rough estimation of tokens
            "text": text
        })
    pdf_document.close()
    return pdf_text