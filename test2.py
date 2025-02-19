import os
import json
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import wave

# Путь к модели Vosk
model_path = r"C:\Users\culdc\Downloads\vosk-model-ru-0.42"  # Замените на путь к вашей модели
audio_path = "audio_tmp.wav"  # Замените на путь к вашему аудиофайлу

# Загрузка модели
if not os.path.exists(model_path):
    print(f"Модель {model_path} не найдена. Скачайте и укажите правильный путь.")
    exit(1)

model = Model(model_path)

# Преобразуем аудио в моно WAV, если это необходимо
audio = AudioSegment.from_file(audio_path)
audio = audio.set_channels(1).set_frame_rate(16000)
audio.export("temp.wav", format="wav")

# Открываем аудиофайл
wf = wave.open("temp.wav", "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
    print("Аудиофайл должен быть в формате mono WAV с частотой 16000 Hz.")
    exit(1)

# Инициализация распознавателя
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)  # Включаем вывод временных меток для слов

# Чтение и обработка аудио
results = []
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        results.append(result)
    else:
        result = json.loads(rec.PartialResult())

# Получаем финальный результат
final_result = json.loads(rec.FinalResult())
results.append(final_result)

# Выводим временные метки слов
for result in results:
    if "result" in result:
        for word_info in result["result"]:
            word = word_info["word"]
            start = word_info["start"]
            end = word_info["end"]
            print(f"Слово: {word}, Начало: {start:.2f}, Конец: {end:.2f}")


