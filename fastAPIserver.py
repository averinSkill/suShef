import os
import wave
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from vosk import Model, KaldiRecognizer
from datetime import datetime


app = FastAPI()

# Папка для сохранения загруженных файлов
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Путь к модели Vosk
model_path = r".\vosk-model-ru-0.42"  # Замените на путь к вашей модели
# Загрузка модели
t0 = datetime.now()
if not os.path.exists(model_path):
    print(f"Модель {model_path} не найдена. Скачайте и укажите правильный путь.")
    exit(1)
print("start model...")
model = Model(model_path)
print("end model...", datetime.now() - t0)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # Сохраняем файл на сервере
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        print("Открываем аудиофайл...")
        wf = wave.open(file_location, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            print("Аудиофайл должен быть в формате mono WAV с частотой 16000 Hz.")
            exit(1)

        print("Инициализация распознавателя")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)  # Включаем вывод временных меток для слов
        print("wf.getframerate()= ", wf.getframerate())
        print("getparams= ", wf.getparams())
        print("getnframes= ", wf.getnframes())
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

        # Возвращаем JSON с именем файла и сообщением об успешной загрузке
        return JSONResponse(content={
            "filename": file.filename,
            "message": "File uploaded successfully",
            "file_location": file_location,
            "result": results
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)