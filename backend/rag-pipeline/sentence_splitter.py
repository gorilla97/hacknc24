from spacy.lang.en import English
from typing import List, Dict
from tqdm.auto import tqdm

def split_into_sentences(text: str) -> List[str]:
    nlp = English()
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    return [str(sent).strip() for sent in doc.sents]

def complete_sentences(pdf_text: List[Dict]) -> List[Dict]:
    for item in tqdm(pdf_text, desc="Splitting into sentences"):
        item["sentences"] = split_into_sentences(item["text"])
        item["page_sentence_count"] = len(item["sentences"])
    return pdf_text