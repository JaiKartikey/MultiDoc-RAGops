from pathlib import Path

from chunker import chunk_text

def main():
    file_path = Path("data/company.txt")

    text = file_path.read_text(encoding="utf-8")

    chunks = chunk_text(text, chunk_size=300, chunk_overlap=50)

    print("The no of chunks:", len(chunks))

    for i, chunk in enumerate(chunks):
        print(f"---chunks{i+1}---")
        print(chunk)

if __name__ == "__main__":
    main()

