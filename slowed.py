import os
import shutil
import time
from pydub import AudioSegment
from pytube import YouTube
from moviepy.editor import *

# Path configurations
temp_audio_folder = "temp_audio_folder"
temp_video_folder = "temp_video_folder"
final_video_folder = "final_video_folder"
song = "Escape"
audio_file = f"{temp_audio_folder}/{song}.mp3"
slowed_song = f"{temp_audio_folder}/{song} slowed.mp3"
video_url = "https://www.youtube.com/watch?v=UNfCvlnsje8"
video_file = f"{final_video_folder}/{song}.mp4"
output_file = f"{final_video_folder}/{song} slowed and reverb.mp4"

def download_youtube_video(url, output_path):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    highest_resolution_stream = streams.first()
    highest_resolution_stream.download(output_path=output_path)
    video_file_name = highest_resolution_stream.default_filename
    return video_file_name

def slow_down_audio(audio_path, output_path):
    sound = AudioSegment.from_file(audio_path)
    slowed_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * 0.85)})
    slowed_sound.export(output_path, format="mp3")

def merge_audio_video(audio_path, video_path, output_path):
    audio = AudioFileClip(audio_path)
    video = VideoFileClip(video_path)
    # Trim the video to 5 seconds
    video = video.subclip(5, 12)

    # Resize the video to the desired resolution (e.g., 720p)
    video = video.resize(height=720)

    # Repeat the trimmed video to match the length of the audio
    video = concatenate_videoclips([video] * int(audio.duration / video.duration))
    video = video.set_audio(audio)
    video.write_videofile(output_path, codec="libx264", audio_codec="libmp3lame", fps=video.fps, preset="ultrafast", bitrate="5000k")

def create_folders():
    os.makedirs(temp_video_folder, exist_ok=True)
    os.makedirs(final_video_folder, exist_ok=True)

def delete_temp_audio():
    shutil.rmtree(temp_audio_folder)
    # Add a delay before deleting the temp_video_folder to ensure the video file is closed properly
    time.sleep(1)
    shutil.rmtree(temp_video_folder)

# Create necessary folders
create_folders()
print("Folder created: ", final_video_folder)

# Download the YouTube video
video_file_name = download_youtube_video(video_url, temp_video_folder)
print("Downloading video done: ", video_file_name)

# Slow down the audio
slow_down_audio(audio_file, slowed_song)
print("Processing audio completed: ", audio_file)

try:
    # Merge audio and video
    merge_audio_video(slowed_song, f"{temp_video_folder}/{video_file_name}", output_file)
    print("Merging processed audio and video")

finally:
    # Clean up temp audio and video folders
    #delete_temp_audio()
    os._exit(1)
