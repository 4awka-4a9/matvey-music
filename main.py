import vosk
import sys
import sounddevice as sd
import json
import queue
import yt_dlp
import subprocess
import os

WAKE_WORD = "матвей"
MODEL_PATH = "model_ru"  
VOLUME = 40              

#словарь исправлений
REPLACEMENTS = {
    "капс айс": "CUPSIZE",
    "кап сайз": "CUPSIZE",
    "кепс айс": "CUPSIZE",
    "капсайз": "CUPSIZE",
    "мэдкид": "madk1d",
    "дырки в штанах": "madk1d дырки в штанах",
    "лиза настя": "CUPSIZE лиза настя"
}

#системные переменные
q = queue.Queue()
try:
    model = vosk.Model(MODEL_PATH)
except:
    print(f"❌ ОШИБКА: Положите модель в папку '{MODEL_PATH}'")
    sys.exit()

samplerate = 16000
current_player = None
    
#матвей говорит
def speak(text):
    clean_text = text.replace('"', '').replace("'", "")
    os.system(f'say -v Milena "{clean_text}"')

def callback(indata, frames, time, status):
    if status: print(status, file=sys.stderr)
    q.put(bytes(indata))

#остоновка музыки
def stop_music():
    global current_player
    if current_player:
        print("🛑 Останавливаю...")
        current_player.kill()
        current_player = None

#включить музыку
def play_music(text_command):
    global current_player, VOLUME
    stop_music()

    # Очистка запроса
    query = text_command.replace(WAKE_WORD, "").replace("включи", "").replace("поставь", "").strip()
    
    # Применяем замены из словаря
    for wrong, right in REPLACEMENTS.items():
        if wrong in query:
            query = query.replace(wrong, right)
    
    if not query: return

    print(f"🔎 Ищу: {query}...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True, # Пропускать заблокированные видео
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            
            url, title = None, None
            for entry in info['entries']:
                if entry: 
                    url = entry['url']
                    title = entry['title']
                    break
            
            if not url:
                print("❌ Ничего не найдено или видео недоступно")
                return

        print(f"🎶 Играет: {title}")
        current_player = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-volume", str(VOLUME), url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"❌ Ошибка YouTube: {e}")

#главный цикл
if __name__ == "__main__":
    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=None, 
                                dtype='int16', channels=1, callback=callback):
            
            rec = vosk.KaldiRecognizer(model, samplerate)
            print(f"🚀 {WAKE_WORD.capitalize()} запущен.")

            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get('text', '')
                    
                    if WAKE_WORD in text:
                        print(f"✨ Команда: {text}")
                        
                        #пауза музыки
                        if "стоп" in text or "выключи" in text or "хватит" in text:
                            speak("Выключаю музыку")
                            stop_music()
                        
                        #вклчение музыки
                        elif "включи" in text or "поставь" in text:
                            speak("Секунду, сейчас найду")
                            play_music(text)

                        #выход
                        elif "закройся" in text:
                            print("До скорой встречи, хозяин!")
                            speak("До скорой встречи, хозяин")
                            sys.exit()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
