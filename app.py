Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import streamlit as st
... from docx import Document
... from docx.enum.text import WD_COLOR_INDEX
... 
... # =========================
... # Hàm đọc dữ liệu từ file Word
... # =========================
... def load_questions(file_path):
...     doc = Document(file_path)
...     questions = []
...     current_q = None
... 
...     for para in doc.paragraphs:
...         text = para.text.strip()
...         if not text:
...             continue
... 
...         # Nếu là câu hỏi
...         if text.lower().startswith("choose") or text.endswith("?"):
...             if current_q:
...                 questions.append(current_q)
...             current_q = {"question": text, "options": []}
... 
...         # Nếu là đáp án
...         elif current_q:
...             # Kiểm tra highlight vàng
...             is_correct = any(
...                 run.font.highlight_color == WD_COLOR_INDEX.YELLOW
...                 for run in para.runs
...             )
...             current_q["options"].append({"text": text, "correct": is_correct})
... 
...     if current_q:
...         questions.append(current_q)
... 
...     return questions
... 

# =========================
# App Streamlit
# =========================
def main():
    st.title("📘 Bài kiểm tra trắc nghiệm tiếng Anh kỹ thuật")

    # Tải câu hỏi
    questions = load_questions("docwise.docx")

    st.write(f"Ngân hàng có {len(questions)} câu hỏi.")

    # Biến lưu đáp án người dùng
    answers = {}

    # Hiển thị câu hỏi
    for i, q in enumerate(questions):
        st.subheader(f"Câu {i+1}: {q['question']}")
        options = [opt["text"] for opt in q["options"]]
        answers[i] = st.radio("Chọn đáp án:", options, index=None, key=f"q{i}")

    # Nút nộp bài
    if st.button("✅ Nộp bài"):
        score = 0
        results = []

        for i, q in enumerate(questions):
            correct_ans = next(opt["text"] for opt in q["options"] if opt["correct"])
            user_ans = answers[i]

            if user_ans == correct_ans:
                score += 1
                results.append((i + 1, True, user_ans, correct_ans))
            else:
                results.append((i + 1, False, user_ans, correct_ans))

        # Hiển thị kết quả tổng
        st.success(f"🎯 Kết quả: {score}/{len(questions)} câu đúng")

        # Hiển thị chi tiết
        st.subheader("📋 Chi tiết kết quả:")
        for q_num, is_correct, user_ans, correct_ans in results:
            if is_correct:
                st.write(f"✅ Câu {q_num}: Đúng ({user_ans})")
            else:
                st.write(f"❌ Câu {q_num}: Sai. Bạn chọn: {user_ans}. Đáp án đúng: {correct_ans}")


if __name__ == "__main__":
    main()
