import moviepy.editor as mp
import speech_recognition as sr
import yt_dlp
from llama_cpp import Llama
from datetime import datetime



def download_video(url, output_path="video_tmp.mp4"):
    # Настройки для yt-dlp
    ydl_opts = {
        'format': 'best',  # Скачать лучшее качество
        'outtmpl': output_path,  # Имя выходного файла
    }

    # Скачивание видео
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def analyze_video(video_path):
    # Загрузите видео
    clip = VideoFileClip(video_path)

    # Пример анализа
    print(f"Длительность видео: {clip.duration} секунд")
    print(f"Разрешение видео: {clip.size}")
    print(f"Частота кадров (FPS): {clip.fps}")

    # Извлечение аудио (если нужно)
    audio = clip.audio
    audio.write_audiofile("audio_tmp.wav")

    # Закройте видео
    clip.close()

def extract_audio_from_video(video_file, audio_file):
    print("Извлечение аудио из видеофайла.")
    #
    video = mp.VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)

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
    except sr.RequestError as e:
        print(f"Ошибка сервиса распознавания; {e}")


def llm_recipe(text):
    print("Start LLM.")
    llm = Llama(
        # model_path = "llama-2-7b-chat.Q4_K_M.gguf",# долгая, но тоже говно
        model_path="./DeepSeek-R1-Distill-Qwen-1.5B-f16.gguf",  # лучшая на сегодня
        # model_path="./DeepSeek-R1-Distill-Qwen-1.5B-Q6_K.gguf", #быстрая, но полное говно
        n_gpu_layers=-1,  # Uncomment to use GPU acceleration
        # seed=1337, # Uncomment to set a specific seed
        n_ctx=2048,  # Uncomment to increase the context window
    )
    output = llm(
        # f"Q: Сделай суммаризацию текста? {text} A: ",
        # f"Выдели ключевые слова {text}", # Prompt
        # # f"О чем текст? {text}", # Prompt
        f"""Q: В тексте есть рецепт приготовления блюда? {text} A: """,  # Prompt
        max_tokens=32,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
        stop=["Q:", "\n"],  # Stop generating just before the model would generate a new question
        echo=True  # Echo the prompt back in the output
    )  # Generate a completion, can also call create_completion

    # print(output['choices'][0]["text"].split("A: \t")[-1])
    print(output['choices'][0]["text"])

    return output


#
if __name__ == "__main__":
    t0 = datetime.now()
    # video_url = "https://rutube.ru/video/e5f6511f905d08cea67a19257a7368af/?r=plemwd"
    video_url = "https://rutube.ru/video/0a5e3a941c8a6a33cd32097e218d6cb2/?r=plemwd"
    # # Скачивание видео
    download_video(video_url, "video_tmp.mp4")

    # # Извлечение аудио из видео
    extract_audio_from_video("video_tmp.mp4", "audio_tmp.wav")

    # Распознавание текста из аудио
    text_from_audio = transcribe_audio_to_text("audio_tmp.wav")
    time_suffix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    text_fln = f"Распознанный_текст_{time_suffix}.txt"
    with open(text_fln, "w", encoding="utf-8") as file:
        file.write(text_from_audio)  # Записываем текст в файл

    answer = llm_recipe(text_from_audio)
    print(answer)
    print(answer['choices'][0]["text"].split("A: \t")[-1])

    print(datetime.now() - t0)

