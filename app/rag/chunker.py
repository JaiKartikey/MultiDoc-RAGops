from app.core.config import settings
def chunk_text(
        text:str , 
        chunk_size:int =settings.chunk_size, 
        chunk_overlap:int = settings.chunk_overlap
        ):


    paragraphs = text.split("\n\n") # creating a list of paragraphs


    chunks = []
    current_chunk =""


    for paragraph in paragraphs:

        paragraph = paragraph.strip()
        if not paragraph:
            continue


        if len(current_chunk) + len(paragraph) <= chunk_size:
            current_chunk += paragraph + "\n\n"

        else:                       #chunk size se bada
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            overlap = current_chunk[-chunk_overlap:]

            current_chunk = overlap + paragraph + "\n\n"

    # agar current_chunk bacha hai

    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks
