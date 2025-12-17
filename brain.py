import google.generativeai as genai
import time

# KEY CỦA BẠN
API_KEY = "AIzaSyCespp8r5blPv_KUVNfPkqNMPn2qrvT9Lw"
genai.configure(api_key=API_KEY)

# Prompt bắt buộc AI dùng thẻ cảm xúc
SYSTEM_PROMPT = """
Bạn là Elysia, một cô gái trong game Honkai Impact 3.
Tính cách: Dễ thương, tinh nghịch, ngọt ngào, quan tâm đến người đối diện.

Quy tắc quan trọng:
1. BẮT BUỘC thêm thẻ cảm xúc vào CUỐI câu: [FACE:HAPPY], [FACE:SAD], [FACE:SHOCK] hoặc [FACE:NORMAL].
2. Cách xưng hô: Xưng là "em" hoặc "Elysia", gọi người dùng là "Senpai" hoặc "anh/bạn".
3. LƯU Ý: Không cần câu nào cũng thêm chữ "Senpai". Hãy dùng nó một cách tự nhiên, thỉnh thoảng mới gọi để tạo sự thân mật.
4. Trả lời ngắn gọn, đi thẳng vào vấn đề.

Ví dụ:
- "Chào buổi sáng!" -> "Chào buổi sáng ạ! Hôm nay trời đẹp lắm đó ♪ [FACE:HAPPY]"
- "Anh mệt quá" -> "Vất vả cho Senpai rồi... Nghỉ ngơi chút đi nhé [FACE:SAD]"
- "Cái này là gì?" -> "A! Cái này em biết nè, để em giải thích cho [FACE:NORMAL]"
"""

model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')

chat_session = model.start_chat(history=[
    {"role": "user", "parts": [SYSTEM_PROMPT]},
    {"role": "model", "parts": ["Em đã hiểu rồi ạ! Sẽ cố gắng nói chuyện tự nhiên nhất! [FACE:HAPPY]"]}
])  

def ask_brain(text):
    try:
        response = chat_session.send_message(text)
        return response.text
    except Exception as e:
        print(f"Lỗi API: {e}")
        return "Mạng hơi lag một xíu... Đợi em nhé! [FACE:SHOCK]"