import streamlit as st
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
import re

def is_all_caps(text):
    """Kiểm tra text có phải toàn chữ hoa (và khoảng trắng/số)"""
    cleaned = text.replace(" ", "").replace(".", "")
    return cleaned.isupper() and len(cleaned) > 2

def is_question(text):
    """Nhận diện câu hỏi"""
    if text.endswith("?"):
        return True
    if "choose the correct group of words" in text.lower():
        return True
    # Câu bắt đầu bằng số và có chữ
    if re.match(r'^\d+\.', text) and not re.search(r'\d+\s*(m|kg|ft|nm)', text.lower()):
        return True
    return False

def load_questions(file_path):
    doc = Document(file_path)
    sections = {}
    current_section = None
    current_q = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Nếu là tiêu đề phụ lục
        if text.lower().startswith("phụ lục"):
            if current_q and current_section:
                sections[current_section].append(current_q)
                current_q = None
            current_section = text
            if current_section not in sections:
                sections[current_section] = []
            continue

        # Nếu là câu hỏi
        if is_question(text):
            if current_q and current_section:
                sections[current_section].append(current_q)
            current_q = {"question": text, "options": []}
            continue

        # Nếu là đáp án rõ ràng (A., B., C., D., E.)
        if current_q and re.match(r'^[A-E]\.', text):
            is_correct = any(
                run.font.highlight_color == WD_COLOR_INDEX.YELLOW
                for run in para.runs
            )
            current_q["options"].append({"text": text, "correct": is_correct})
            continue

        # Nếu là đáp án kiểu in hoa hoặc mô tả sau câu hỏi
        if current_q and (is_all_caps(text) or not is_question(text)):
            is_correct = any(
                run.font.highlight_color == WD_COLOR_INDEX.YELLOW
                for run in para.runs
            )
            current_q["options"].append({"text": text, "correct": is_correct})
            continue

    if current_q and current_section:
        sections[current_section].append(current_q)

    return sections


def main():
    st.title("📘 Bài kiểm tra trắc nghiệm tiếng Anh kỹ thuật")

    sections = load_questions("docwise.docx")
    section_names = [s for s in sections.keys() if s.lower().startswith("phụ lục")]

    chosen_section = st.selectbox("👉 Bạn muốn làm phần nào?", [""] + section_names)

    if not chosen_section:
        st.info("Hãy chọn một phụ lục để bắt đầu.")
        return

    questions = sections[chosen_section]
    if not questions:
        st.warning(f"❌ Không có câu hỏi nào trong {chosen_section}")
        return

    st.write(f"🔎 Đang làm: **{chosen_section}** ({len(questions)} câu hỏi)")

    # Form quiz
    with st.form("quiz_form"):
        answers = {}
        for i, q in enumerate(questions, start=1):  # đánh số lại từ 1
            st.subheader(f"Câu {i}: {q['question']}")
            options = [opt["text"] for opt in q["options"]]
            if not options:
                st.warning(f"Câu {i} chưa có đáp án, bỏ qua.")
                continue
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

        for i, q in enumerate(questions, start=1):
            opts = q["options"]
            if not opts or i not in answers:
                continue
            correct_options = [opt["text"] for opt in opts if opt["correct"]]
            if not correct_options:
                continue
            correct_ans = correct_options[0]
            user_ans = answers[i]

            if user_ans == correct_ans:
                score += 1
                results.append((i, True, user_ans, correct_ans))
            else:
                results.append((i, False, user_ans, correct_ans))

        st.success(f"🎯 Kết quả: {score}/{len(questions)} câu đúng")

        st.subheader("📋 Chi tiết kết quả:")
        for q_num, is_correct, user_ans, correct_ans in results:
            if is_correct:
                st.write(f"✅ Câu {q_num}: Đúng ({user_ans})")
            else:
                st.write(f"❌ Câu {q_num}: Sai. Bạn chọn: {user_ans}. Đáp án đúng: {correct_ans}")


if __name__ == "__main__":
    main()
