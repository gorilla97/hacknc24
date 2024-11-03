def read_text_from_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def write_to_notepad(text: str, output_path: str):
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)