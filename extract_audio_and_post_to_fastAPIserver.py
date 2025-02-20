import moviepy.editor as mp
from pydub import AudioSegment
import yt_dlp
import requests
import json
from datetime import datetime




def download_video(url, output_path):
    # Настройки для yt-dlp
    ydl_opts = {
        'format': 'best',  # Скачать лучшее качество
        'outtmpl': output_path,  # Имя выходного файла
    }
    print("Скачивание видео...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def extract_audio_from_video(video_file, audio_file):
    print(f"Извлечение аудио из видеофайла и сохранение в {audio_file}.")
    video = mp.VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file, fps=16000, codec='pcm_s16le')
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(audio_file, format="wav")
    # return video.duration

time_suffix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
video_tmp_file = f"video_tmp_{time_suffix}.mp4"
audio_tmp_file = f"audio_tmp_{time_suffix}.wav"  # Укажите путь к вашему аудиофайлу

# video_url = "https://rutube.ru/video/e5f6511f905d08cea67a19257a7368af/?r=plemwd"
video_url = "https://vt.tiktok.com/ZSMYVG3W6/"

t0 = datetime.now()
download_video(video_url, video_tmp_file)
print(f"Скачивание видео заняло {datetime.now() - t0}")

t0 = datetime.now()
extract_audio_from_video(video_tmp_file, audio_tmp_file)
print(f"Извлечение аудио заняло {datetime.now() - t0}")

url = "http://127.0.0.1:8000/upload-audio/"


# Открываем файл и отправляем его на сервер
with open(audio_tmp_file, "rb") as file:
    files = {"file": (audio_tmp_file, file, "audio/mpeg")}
    headers = {
        "accept": "application/json"
    }
    print("Послал файл...")
    t0 = datetime.now()
    response = requests.post(url, files=files, headers=headers)

# Выводим ответ от сервера
print(response.status_code)
json_formatted_str = json.dumps(response.json(), indent=4, ensure_ascii=False)
print(json_formatted_str)
print(f"Ответ пришел через {datetime.now() - t0}")

with open('subtitles_results.json', 'w') as fp:
    json.dump(response.json(), fp)

