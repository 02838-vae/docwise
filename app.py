import streamlit as st
from docx import Document
from docx.enum.text import WD_COLOR_INDEX

# =========================
# Hàm đọc dữ liệu từ file Word và chia theo phụ lục
# =========================
def load_questions(file_path):
    doc = Document(file_path)
    sections = {}
    current_section = "Chung"
    current_q = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Nhận diện tiêu đề phụ lục
        if text.lower().startswith("phụ lục"):
            current_section = text
            if current_section not in sections:
                sections[current_section] = []
            continue

        # Nhận diện câu hỏi
        if text.lower().startswith("choose") or text.endswith("?"):
            if current_q:
                sections[current_section].append(current_q)
            current_q = {"question": text, "options": []}
            continue

        # Nhận diện đáp án
        if current_q:
            is_correct = any(
                run.font.highlight_color == WD_COLOR_INDEX.YELLOW
                for run in para.runs
            )
            current_q["options"].append({"text": text, "correct": is_correct})

    # Thêm câu hỏi cuối cùng
    if current_q:
        sections[current_section].append(current_q)

    return sections


# =========================
# App Streamlit
# =========================
def main():
    st.title("📘 Bài kiểm tra trắc nghiệm tiếng Anh kỹ thuật")

    # Load ngân hàng câu hỏi
    sections = load_questions("docwise.docx")
    section_names = list(sections.keys())

    # Người dùng chọn phần muốn làm
    st.sidebar.header("Chọn phần thi")
    chosen_section = st.sidebar.selectbox("Bạn muốn làm phần nào?", section_names)

    if not chosen_section:
        st.warning("Hãy chọn một phụ lục ở thanh bên trái!")
        return

    questions = sections[chosen_section]
    st.write(f"🔎 Bạn đang làm: **{chosen_section}** ({len(questions)} câu hỏi)")

    # Lưu đáp án trong session_state để không bị reset khi chọn
    if "answers" not in st.session_state:
        st.session_state["answers"] = {}

    # Hiển thị câu hỏi
    for i, q in enumerate(questions):
        st.subheader(f"Câu {i+1}: {q['question']}")
        options = [opt["text"] for opt in q["options"]]
        st.session_state["answers"][i] = st.radio(
            "Chọn đáp án:",
            options,
            index=None,
            key=f"{chosen_section}_q{i}"
        )

    # Nút nộp bài
    if st.button("✅ Nộp bài"):
        score = 0
        results = []

        for i, q in enumerate(questions):
            correct_ans = next(opt["text"] for opt in q["options"] if opt["correct"])
            user_ans = st.session_state["answers"].get(i)

            if user_ans == correct_ans:
                score += 1
                results.append((i + 1, True, user_ans, correct_ans))
            else:
                results.append((i + 1, False, user_ans, correct_ans))

        # Kết quả tổng
        st.success(f"🎯 Kết quả: {score}/{len(questions)} câu đúng")

        # Chi tiết từng câu
        st.subheader("📋 Chi tiết kết quả:")
        for q_num, is_correct, user_ans, correct_ans in results:
            if is_correct:
                st.write(f"✅ Câu {q_num}: Đúng ({user_ans})")
            else:
                st.write(f"❌ Câu {q_num}: Sai. Bạn chọn: {user_ans}. Đáp án đúng: {correct_ans}")


if __name__ == "__main__":
    main()
