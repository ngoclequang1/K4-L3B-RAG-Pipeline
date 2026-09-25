"""Streamlit chat interface for the VinUniversity student-information RAG."""

import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(page_title="VinUni Student RAG", page_icon="🎓", layout="wide")


def show_sources(sources: list[dict], retrieval_source: str) -> None:
    if not sources:
        return
    with st.expander(f"Nguồn tham khảo · {retrieval_source}", expanded=False):
        for index, source in enumerate(sources, 1):
            metadata = source["metadata"]
            st.markdown(f"**[Document {index}] {metadata['title']}**")
            url = metadata.get("url")
            if url:
                st.markdown(f"[{metadata['source']}]({url})")
            else:
                st.caption(metadata["source"])
            st.caption(
                f"Phương thức: {source['retrieval_method']} · "
                f"Điểm: {source['score']:.4f} · Chunk: {metadata['chunk_index']}"
            )
            st.write(source["content"][:500] + ("…" if len(source["content"]) > 500 else ""))


if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("VinUni Student RAG")
    st.caption("Tra cứu quy định, hoạt động và dịch vụ dành cho sinh viên VinUniversity.")
    top_k = st.slider("Số đoạn tài liệu", 3, 10, 5)
    if st.button("Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("VinUni Student Information Assistant")
st.caption("Câu trả lời được tạo từ bộ tài liệu của nhóm và luôn kèm nguồn có thể kiểm tra.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            show_sources(message.get("sources", []), message.get("retrieval_source", "none"))

query = st.chat_input("Nhập câu hỏi về chính sách hoặc đời sống sinh viên...")
if query:
    user_message = {"role": "user", "content": query}
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm trong tài liệu..."):
            try:
                result = generate_with_citation(query, top_k=top_k)
            except Exception as error:
                result = {
                    "answer": f"Không thể xử lý câu hỏi lúc này: {error}",
                    "sources": [],
                    "retrieval_source": "none",
                }
        st.markdown(result["answer"])
        show_sources(result["sources"], result["retrieval_source"])
    st.session_state.messages.append({"role": "assistant", "content": result["answer"], **result})
