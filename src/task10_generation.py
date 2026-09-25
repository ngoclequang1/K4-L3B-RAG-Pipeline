"""Task 10 - grounded answer generation with inspectable citations."""

import os
import re

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "extractive").casefold()
LLM_MODEL = os.getenv("LLM_MODEL", "")
SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Trích dẫn nguồn bằng nhãn [Document N] sau từng khẳng định. Nếu context không
đủ bằng chứng, trả lời rằng không thể xác minh; không suy đoán."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Place highly ranked chunks at context edges without mutating input."""
    if len(chunks) <= 2:
        return list(chunks)
    return list(chunks[::2]) + list(reversed(chunks[1::2]))


def format_context(chunks: list[dict]) -> str:
    """Format chunks with stable labels, titles, sources, and optional URLs."""
    parts: list[str] = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        url = metadata.get("url") or "N/A"
        parts.append(
            f"[Document {index} | Title: {metadata['title']} | "
            f"Source: {metadata['source']} | URL: {url}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def _extractive_answer(user_message: str) -> str:
    """Produce a conservative offline answer from the first context passages."""
    context = user_message.split("\n\nQuestion:", 1)[0]
    blocks = context.split("\n\n---\n\n")
    statements: list[str] = []
    for index, block in enumerate(blocks[:3], 1):
        body = block.split("]\n", 1)[-1]
        paragraphs = [
            re.sub(r"\s+", " ", paragraph).strip(" #-*")
            for paragraph in re.split(r"\n\s*\n", body)
        ]
        sentence = next(
            (paragraph for paragraph in paragraphs if len(paragraph) >= 40 and not paragraph.startswith("http")),
            "",
        )
        if sentence:
            statements.append(f"{sentence} [Document {index}]")
        if len(statements) == 2:
            break
    return "\n\n".join(statements) if statements else SAFE_REFUSAL


def call_llm(system_prompt: str, user_message: str) -> str:
    """Dispatch generation to the configured provider and return plain text."""
    if LLM_PROVIDER in {"extractive", "offline", "local"}:
        return _extractive_answer(user_message)
    if LLM_PROVIDER == "openai":
        from openai import OpenAI

        response = OpenAI().responses.create(
            model=LLM_MODEL or "gpt-4o-mini",
            instructions=system_prompt,
            input=user_message,
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.output_text.strip()
    if LLM_PROVIDER == "gemini":
        from google import genai
        from google.genai import types

        response = genai.Client().models.generate_content(
            model=LLM_MODEL or "gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=TEMPERATURE,
                top_p=TOP_P,
            ),
        )
        return (response.text or "").strip()
    if LLM_PROVIDER == "anthropic":
        from anthropic import Anthropic

        response = Anthropic().messages.create(
            model=LLM_MODEL or "claude-3-5-haiku-latest",
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1000,
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return "".join(block.text for block in response.content if block.type == "text").strip()
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Retrieve evidence, generate an answer, and return GenerationResult."""
    query = query.strip()
    if not query:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    sources = reorder_for_llm(chunks)
    context = format_context(sources)
    try:
        answer = call_llm(SYSTEM_PROMPT, f"Context:\n{context}\n\nQuestion: {query}")
    except Exception:
        answer = SAFE_REFUSAL
    if not answer.strip():
        answer = SAFE_REFUSAL
    for citation in re.findall(r"\[Document (\d+)\]", answer):
        if int(citation) > len(sources):
            answer = SAFE_REFUSAL
            break
    method = sources[0]["retrieval_method"]
    retrieval_source = "pageindex" if method == "pageindex" else "hybrid"
    return {"answer": answer, "sources": sources, "retrieval_source": retrieval_source}


if __name__ == "__main__":
    print(generate_with_citation("How many active members does a club need?"))
