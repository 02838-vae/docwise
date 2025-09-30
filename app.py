import streamlit as st
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
import re

# =========================
# Hàm đọc dữ liệu từ file Word, chia theo phụ lục
# =========================
def load_questions(file_path):
    doc = Document(file_path)
    sections = {}
    current_section = None
    current_q = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Nếu gặp tiêu đề phụ lục
        if text.lower().startswith("phụ lục"):
            current_section = text
            if current_section not in sections:
                sections[current_section] = []
            current_q = None
            continue

        # Nếu là câu hỏi (bắt đầu bằng số)
        if re.match(r'^\d+\.', text):
            if current_q:  # lưu câu trước đó
                sections[current_section].append(current_q)
            current_q = {"question": text, "options": []}
            continue

        # Nếu là đáp án (A., B., C., D., E.)
        if current_q and re.match(r'^[A-E]\.', text):
            is_correct = any(
                run.font.highlight_color == WD_COLOR_INDEX.YELLOW
                for run in para.runs
            )
            current_q["options"].append({"text": text, "correct": is_correct})

    # Thêm câu hỏi cuối cùng
    if current_q and current_section:
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

    # Bắt buộc chọn phụ lục trước
    chosen_section = st.selectbox("👉 Bạn muốn làm phần nào?", [""] + section_names)

    if not chosen_section:
        st.info("Hãy chọn một phụ lục để bắt đầu.")
        return

    questions = sections[chosen_section]
    st.write(f"🔎 Đang làm: **{chosen_section}** ({len(questions)} câu hỏi)")

    # Gom câu hỏi trong form để tránh reload từng click
    with st.form("quiz_form"):
        answers = {}
        for i, q in enumerate(questions):
            st.subheader(f"Câu {i+1}: {q['question']}")
            options = [opt["text"] for opt in q["options"]]
            answers[i] = st.radio(
                "Chọn đáp án:",
                options,
                index=None,
                key=f"{chosen_section}_q{i}"
            )

        submitted = st.form_submit_button("✅ Nộp bài")

    if submitted:
        score = 0
        results = []

        for i, q in enumerate(questions):
            if not q["options"]:
                continue
            correct_ans = next(opt["text"] for opt in q["options"] if opt["correct"])
            user_ans = answers[i]

            if user_ans == correct_ans:
                score += 1
                results.append((i + 1, True, user_ans, correct_ans))
            else:
                results.append((i + 1, False, user_ans, correct_ans))

        # Tổng điểm
        st.success(f"🎯 Kết quả: {score}/{len(questions)} câu đúng")

        # Chi tiết
        st.subheader("📋 Chi tiết kết quả:")
        for q_num, is_correct, user_ans, correct_ans in results:
            if is_correct:
                st.write(f"✅ Câu {q_num}: Đúng ({user_ans})")
            else:
                st.write(f"❌ Câu {q_num}: Sai. Bạn chọn: {user_ans}. Đáp án đúng: {correct_ans}")


if __name__ == "__main__":
    main()
