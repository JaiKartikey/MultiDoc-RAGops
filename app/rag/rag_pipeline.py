import os

from openai import OpenAI

from app.rag.ingest import ingest_document
from app.core.logger import get_logger
from app.core.config import settings    

logger = get_logger(__name__)

client = OpenAI(
    api_key=settings.gemini_api_key,
    base_url=settings.gemini_api_base_url
)

# ----------------generate answer------------------[[[ context + question === > answer ]]]-----------------------------
def generate_answer(question, context):
    """
    Ask Gemini to answer using retrieved context.
    """

    prompt = f"""
You are a helpful document assistant.

Answer the user's question using ONLY
the provided context.

If the answer cannot be found in the context,
say that you don't have enough information.

Context:
{context}

Question:
{question}
"""
    logger.info("Getting response from Gemini ")

    response = client.chat.completions.create(
        model="gemini-3.5-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# -----------------ask question------------------[[[ gets similar result ---> context -----> generates answer]]]-----------------------------
def ask_question(vector_store, question):
    """
    Complete RAG flow:

    Question
        ↓
    Retrieval
        ↓
    Context
        ↓
    Gemini
        ↓
    Answer
    """

    results = vector_store.search(
        question,
        top_k=settings.top_k
    )

    context = "\n\n".join(
        result["chunk"]
        for result in results
    )

    answer = generate_answer(
        question,
        context
    )

    return answer, results
