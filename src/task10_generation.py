"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
from dotenv import load_dotenv
from .task9_retrieval_pipeline import retrieve

load_dotenv()

TOP_K = 5
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "Bạn là một trợ lý RAG chuyên nghiệp. Nhiệm vụ của bạn là trả lời câu hỏi dựa TRỰC TIẾP "
    "trên ngữ cảnh (Context) được cung cấp. Hãy trích dẫn rõ tên tài liệu/nguồn (Title/Source) "
    "khi đưa ra thông tin. Nếu trong ngữ cảnh không có thông tin, hãy trả lời: "
    "'Tôi không thể xác minh thông tin này từ nguồn hiện có.'"
)


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (giảm hiện tượng lost-in-the-middle)."""
    if len(chunks) <= 2:
        return list(chunks)
    
    # Chia danh sách thành các vị trí lẻ và chẵn
    front = chunks[::2]
    back = chunks[1::2]
    
    # Đảo ngược nửa sau để chunk có rank cao nhất nằm ở 2 đầu
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label để LLM trích dẫn."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Unknown Title")
        source = metadata.get("source", "Unknown Source")
        
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n"
            f"{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình LLM_PROVIDER trong .env."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()
    model_name = os.getenv("LLM_MODEL", LLM_MODEL)

    # 1. Nhánh OpenAI
    if provider == "openai":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Lỗi: Chưa cấu hình OPENAI_API_KEY trong file .env."
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    # 2. Nhánh Gemini (Google GenAI)
    elif provider == "gemini":
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Lỗi: Chưa cấu hình GEMINI_API_KEY trong file .env."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name if "gemini" in model_name else "gemini-1.5-flash",
            system_instruction=system_prompt,
        )
        response = model.generate_content(user_message)
        return response.text.strip()

    # 3. Nhánh Anthropic (Claude)
    elif provider == "anthropic":
        from anthropic import Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "Lỗi: Chưa cấu hình ANTHROPIC_API_KEY trong file .env."
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model_name if "claude" in model_name else "claude-3-haiku-20240307",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text.strip()

    # Fallback / Mock nếu provider không hợp lệ hoặc dùng môi trường test local
    else:
        return (
            "Dựa trên các tài liệu được cung cấp, tôi đã tìm thấy thông tin phù hợp "
            "nhưng hệ thống đang chạy ở chế độ offline/mock provider."
        )


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult gồm câu trả lời, nguồn tham khảo và retrieval method."""
    chunks = retrieve(query, top_k=top_k)
    
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    # Sắp xếp lại thứ tự chunk chống Lost-in-the-middle
    reordered = reorder_for_llm(chunks)
    
    # Format ngữ cảnh đưa vào LLM
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    
    # Gọi LLM sinh câu trả lời
    answer = call_llm(SYSTEM_PROMPT, user_message)
    
    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0].get("retrieval_method", "unknown"),
    }


if __name__ == "__main__":
    result = generate_with_citation("Thời gian hoàn trả hàng là bao lâu?")
    print("Answer:\n", result["answer"])
    print("\nRetrieval Source:", result["retrieval_source"])
    print("\nNumber of sources:", len(result["sources"]))
