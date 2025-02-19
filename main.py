import moviepy.editor as mp
import speech_recognition as sr
import yt_dlp
from llama_cpp import Llama
from datetime import datetime
import os
# pip install git+https://github.com/openai/whisper.git


def download_video(url, output_path):
    # Настройки для yt-dlp
    ydl_opts = {
        'format': 'best',  # Скачать лучшее качество
        'outtmpl': output_path,  # Имя выходного файла
    }
    # Скачивание видео
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def extract_audio_from_video(video_file, audio_file):
    print("Извлечение аудио из видеофайла.")
    video = mp.VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)
    return video.duration

def transcribe_audio_to_text(audio_file):
    print("Инициализация распознавателя.")
    recognizer = sr.Recognizer()

    print("Загрузка аудиофайла")
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)  # Запись аудио

    print("Распознавание текста из аудио")
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")  # Используем Google Web Speech API
        print("Распознанный текст: " + text)
        return text
    except sr.UnknownValueError:
        print("Речь не распознана")
        return "Could not understand audio"
    except sr.RequestError as e:
        print(f"Ошибка сервиса распознавания; {e}")
        return "API unavailable"


# Add subtitles to the video
def add_subtitles(video_path, output_path, text, duration):
    video = VideoFileClip(video_path)
    subtitles = TextClip(text, fontsize=24, color="white", bg_color="black", size=video.size)
    subtitles = subtitles.set_position(("center", "bottom")).set_duration(duration)
    final_video = CompositeVideoClip([video, subtitles])
    final_video.write_videofile(output_path, codec="libx264")

# Main function
def auto_subtitles(video_path, output_path):
    # Extract audio
    audio_path = "temp_audio.wav"
    duration = extract_audio(video_path, audio_path)

    # Transcribe audio
    text = transcribe_audio(audio_path)
    print("Transcribed Text:", text)

    # Add subtitles to video
    add_subtitles(video_path, output_path, text, duration)

    # Clean up temporary files
    os.remove(audio_path)


def llm_recipe(text):
    print("Start LLM.")
    llm = Llama(
        model_path="Parm2-Qwen2.5-3B.Q4_K_M.gguf",  # Идеал
        # model_path = "llama-2-7b-chat.Q4_K_M.gguf",# долгая, но тоже говно
        # model_path="./DeepSeek-R1-Distill-Qwen-1.5B-f16.gguf",  # лучшая на сегодня
        # model_path="./DeepSeek-R1-Distill-Qwen-1.5B-Q6_K.gguf", #быстрая, но полное говно
        n_gpu_layers=-1,  # Uncomment to use GPU acceleration
        # seed=1337, # Uncomment to set a specific seed
        n_ctx=2048,  # Uncomment to increase the context window
    )
    output = llm(
        f"Q: Сделай суммаризацию текста на русском языке? {text} A: ",
        # f"Q: Выдели ключевые слова {text} A: ", # Prompt
        # f"Q: Сделать резюме. {text} A: ", # Prompt
        # f"""Q: В тексте есть рецепт приготовления блюда? {text} A: """,  # Prompt
        max_tokens=62,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
        stop=["Q:", "\n"],  # Stop generating just before the model would generate a new question
        echo=True  # Echo the prompt back in the output
    )  # Generate a completion, can also call create_completion

    # print(output['choices'][0]["text"].split("A: \t")[-1])
    print(output['choices'][0]["text"])

    return output


#
if __name__ == "__main__":
    t0 = datetime.now()

    time_suffix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # video_url = "https://vt.tiktok.com/ZSMYVG3W6/"
    video_url = "https://rutube.ru/video/e5f6511f905d08cea67a19257a7368af/?r=plemwd"
    # video_url = "https://rutube.ru/video/b905e18ba0bb9badfac516f30b57f77b/"
    # # Скачивание видео
    download_video(video_url, f"video_tmp_{time_suffix}.mp4")

    # # Извлечение аудио из видео
    extract_audio_from_video(f"video_tmp_{time_suffix}.mp4", f"audio_tmp_{time_suffix}.wav")

    # Распознавание текста из аудио
    text_from_audio = transcribe_audio_to_text(f"audio_tmp_{time_suffix}.wav")
    text_fln = f"Распознанный_текст_{time_suffix}.txt"
    with open(text_fln, "w", encoding="utf-8") as file:
        file.write(text_from_audio)  # Записываем текст в файл

    answer = llm_recipe(text_from_audio)
    print(answer)
    print(answer['choices'][0]["text"].split("A:")[-1])

    search_text = "рецепт"
    if search_text in answer['choices'][0]["text"].split("A:")[-1]:
        print(f"Текст '{search_text}' найден в аудиозаписи.")
    else:
        print(f"Текст '{search_text}' не найден в аудиозаписи.")
    print(datetime.now() - t0)


# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
#
# # Пример: обрезка видео с 10-й по 20-ю секунду
# ffmpeg_extract_subclip("ваше_видео.mp4", 10, 20, targetname="этап_1.mp4")
