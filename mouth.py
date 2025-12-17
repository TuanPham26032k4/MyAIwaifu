import edge_tts
import pygame
import asyncio

# Giọng chị Google
VOICE = "vi-VN-HoaiMyNeural" 
OUTPUT_FILE = "response.mp3"

async def speak(text):
    # Loại bỏ thẻ cảm xúc để không đọc lên thành tiếng
    clean_text = text.split("[FACE")[0].strip()
    
    print(f">> Elysia nói: {clean_text}")

    # --- CÔNG THỨC GIỌNG ELYSIA ---
    # Pitch +30Hz: Giọng cao, trong trẻo
    # Rate +10%: Tốc độ vừa phải, quyến rũ
    communicate = edge_tts.Communicate(clean_text, VOICE, rate="+10%", pitch="+30Hz")
    
    await communicate.save(OUTPUT_FILE)
    
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Lỗi loa: {e}")

def say(text):
    try:
        asyncio.run(speak(text))
    except:
        pass