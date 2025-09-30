import streamlit as st
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
import re

# =========================
# Hàm đọc dữ liệu từ file Word, chia theo phụ lục
# =========================
def load_questions(file_path):
    doc = Document(file_path)
    sections = {"Chung": []}
    current_section = "Chung"
    current_q = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Nhận diện tiêu đề phụ lục
        if text.lower().startswith("phụ lục"):
            if current_q:
                sections[current_section].append(current_q)
                current_q = None
            current_section = text
            if current_section not in sections:
                sections[current_section] = []
            continue

        # Nhận diện câu hỏi (bắt đầu bằng số.)
        if re.match(r'^\d+\.', text):
            if current_q:
                sections[current_section].append(current_q)
            current_q = {"question": text, "options": []}
            continue

        # Nhận diện đáp án (A., B., C., D., E.)
        if current_q and re.match(r'^[A-E]\.', text):
            is_correct = any(
                run.font.highlight_color == WD_COLOR_INDEX.YELLOW
                for run in para.runs
            )
            current_q["options"].append({"text": text, "correct": is_correct})

    # Push câu hỏi cuối cùng
    if current_q:
        sections[current_section].append(current_q)

    return sections


# =========================
# App Streamlit
# =========================
def main():
    st.title("📘 Bài kiểm tra trắc nghiệm tiếng Anh kỹ thuật")

    sections = load_questions("docwise.docx")
    section_names = list(sections.keys())

    # Debug mode toggle
    debug = st.sidebar.checkbox("🔍 Debug mode (hiển thị parser raw)")

    chosen_section = st.selectbox("👉 Bạn muốn làm phần nào?", [""] + section_names)

    if not chosen_section:
        st.info("Hãy chọn một phụ lục để bắt đầu.")
        return

    questions = sections[chosen_section]
    st.write(f"🔎 Đang làm: **{chosen_section}** ({len(questions)} câu hỏi)")

    # Nếu bật debug mode thì chỉ hiển thị kết quả parse
    if debug:
        st.subheader("🛠 Kết quả parser đọc được:")
        for i, q in enumerate(questions, start=1):
            st.write(f"**{i}. {q['question']}**")
            for opt in q["options"]:
                if opt["correct"]:
                    st.write(f"✅ {opt['text']}")
                else:
                    st.write(f"❌ {opt['text']}")
        return  # Không hiện form làm bài nữa

    # Bình thường thì hiển thị form làm bài
    with st.form("quiz_form"):
        answers = {}
        for i, q in enumerate(questions):
            st.subheader(q["question"])
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
                results.append((q["question"], True, user_ans, correct_ans))
            else:
                results.append((q["question"], False, user_ans, correct_ans))

        st.success(f"🎯 Kết quả: {score}/{len(questions)} câu đúng")

        st.subheader("📋 Chi tiết kết quả:")
        for q_text, is_correct, user_ans, correct_ans in results:
            if is_correct:
                st.write(f"✅ {q_text} → Đúng ({user_ans})")
            else:
                st.write(f"❌ {q_text} → Sai. Bạn chọn: {user_ans}. Đáp án đúng: {correct_ans}")


if __name__ == "__main__":
    main()
