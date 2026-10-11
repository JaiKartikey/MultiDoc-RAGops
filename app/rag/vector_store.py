import numpy as np
import json
import faiss 


from pathlib import Path

from app.rag.embeddings import create_embedding

from app.core.logger import get_logger

logger = get_logger(__name__)

# 1---------------------- initiallizing
class VectorStore:
    def __init__(self):
        self.index =None
        self.chunks = []



# 2-----------------------chunks to embedding
    def build(self, chunks):
        self.chunks =chunks

        embeddings =[]

        logger.info("creating embeddings for %d chunks", len(chunks))

        for chunk in chunks:
            embedding =create_embedding(chunk)
            embeddings.append(embedding)



# 3----------------------- list to array
        # converting the python list to numpy array
        embeddings = np.array(
            embeddings, 
            dtype ="float32"
        )




# 4-----------------------dimention +index
        # number of dimension in each embedding
        dimension = embeddings.shape[1]

        # creating a FAISS index
        self.index = faiss.IndexFlatIP(dimension)

# 5 -------------------------normalize

        # normalize vector so inner products behaves like cosine similarity
        faiss.normalize_L2(embeddings)


# 6 -------------------------- indexing +embedding

        # index + embeddings
        self.index.add(embeddings)

    def add_chunks(self, new_chunks):
        if not new_chunks:
            return 0

        if self.index is None:
            self.build(new_chunks)
            return len(new_chunks)

        logger.info("adding embeddings for %d new chunks", len(new_chunks))
        new_embeddings = []
        for chunk in new_chunks:
            embedding = create_embedding(chunk)
            new_embeddings.append(embedding)

        embeddings = np.array(new_embeddings, dtype="float32")
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)
        self.chunks.extend(new_chunks)

        logger.info("Total chunks in vector store: %d", len(self.chunks))
        return len(new_chunks)




    def save(self, path:str):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)  #creates a directory


        # 4-5 The FAISS index contains the vectors that FAISS uses for similarity search.
        index_path = path / "index.faiss"
        chunks_path = path / "chunks.json"

        #  index.faiss
        #     ↓
        # "Vector #17 is the most similar"
        #     ↓
        # chunks.json
        #     ↓
        # "Vector #17 corresponds to this actual piece of text"

        
        #6. Save the FAISS index (where the actual FAISS index gets saved.)

        faiss.write_index(
            self.index,   #might contain thousands of embeddings:
            str(index_path)  #FAISS expects a file path, so we convert it to str
        )

        # 7. Open the chunks JSON file

        with open(chunks_path, "w", encoding="utf-8") as file:   # opens chunks.json   allows storing é ह 中 文 😊
            #8. Convert chunks into JSON

            json.dump(
                self.chunks, file, ensure_ascii=False, indent=2
                #takes self.chunks to save it to chunks.json ----unicode readable ----indent will make nicely formatted
            )

        #9. Log that saving succeeded
        logger.info("Successfully save the chunks to %s",path)


    def load(self, path:str):
        path = Path(path)

        index_path = path / "index.faiss"
        chunks_path = path / "chunks.json"

        if not index_path.exists():
            raise ValueError("Faiss index not found")

        if not chunks_path.exists():
            raise ValueError("Chunks do not exists")


        #load the faiss index
        #     disk
        #       ↓
        # index.faiss
        #       ↓
        # FAISS index
        #       ↓
        # self.index

        self.index = faiss.read_index( str(index_path) )

        with open(chunks_path, "r" ,encoding="utf-8") as file:
            self.chunks = json.load(file)

        logger.info("Successfully loaded from %s", path)



    def search(self, query, top_k =5):

        #edge cases: empty store
        if self.index is None or not self.chunks:
            logger.info("Search requested but vector store is empty.")
            return []

        # -----------------------------------------
        top_k = min(top_k, len(self.chunks))

        logger.info("Searching for query: %s", query)

        # ----------------------------------------

        #1 creating embedding
        query_embedding = create_embedding(query)

        #2 embedding list to array
        query_embedding = np.array(
            [query_embedding],
            dtype= "float32"
        )

        #3 dimension + index + normalize
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        result =[]

        for score, index in zip( scores[0], indices[0] ):
            result.append({
                "chunk": self.chunks[index],
                "score": float(score)
            })

        logger.info("Retrieved %d chunks", len(result))
        return result


