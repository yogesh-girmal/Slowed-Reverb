import os
import shutil
import time
from pydub import AudioSegment
from pytube import YouTube
from moviepy.editor import *
import numpy as np
from pedalboard import Reverb
from pedalboard.io import AudioFile

audio_folder = "audio_folder"
temp_audio_folder = "temp_audio_folder"
temp_video_folder = "temp_video_folder"
final_video_folder = "final_video_folder"
video_url = "https://www.youtube.com/watch?v=UNfCvlnsje8"

def add_reverb_to_audio(infile, outfile):
    # Load the audio file
    audio = AudioSegment.from_file(infile)

    # Slow down the audio by 10%
    slow_factor = 0.85
    slow_audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * slow_factor)
    })

    # Convert the AudioSegment to a numpy array (32-bit float format)
    audio_array = np.array(slow_audio.get_array_of_samples(), dtype=np.float32) / 32768.0

    # Create a Reverb instance with adjusted parameters for cleaner audio
    reverb = Reverb(room_size=0.6, damping=0.6, wet_level=0.3, dry_level=0.4, width=0.3)

    # Apply the reverb effect to the audio array
    effect_array = reverb(audio_array, slow_audio.frame_rate)

    # Convert the modified audio array back to an AudioSegment
    effect_audio = slow_audio._spawn((effect_array * 32768.0).astype(np.int16))

    # Export the modified audio to an MP3 file
    effect_audio.export(outfile, format='mp3')

def download_youtube_video(url, output_path):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    highest_resolution_stream = streams.first()
    highest_resolution_stream.download(output_path=output_path)
    video_file_name = highest_resolution_stream.default_filename
    return video_file_name

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

def delete_temp_audio_video():
    # shutil.rmtree(temp_audio_folder)
    # Add a delay before deleting the temp_video_folder to ensure the video file is closed properly
    time.sleep(1)
    shutil.rmtree(temp_video_folder)

# Create necessary folders
create_folders()
print("Folder created: ", final_video_folder)

# Download the YouTube video
video_file_name = download_youtube_video(video_url, temp_video_folder)
print("Downloading video done: ", video_file_name)

# Get the list of audio files in the audio_folder
audio_files = os.listdir(audio_folder)

for audio_file in audio_files:
    # Construct file paths
    song = os.path.splitext(audio_file)[0]
    audio_path = os.path.join(audio_folder, audio_file)
    slowed_song = os.path.join(temp_audio_folder, f"{song} slowed.mp3")
    video_file = os.path.join(final_video_folder, f"{song}.mp4")
    output_file = os.path.join(final_video_folder, f"{song} slowed and reverb.mp4")


    # Add reverb to the audio
    add_reverb_to_audio(audio_path, slowed_song)
    print("Adding reverb to audio completed: ", audio_path)

    try:
        # Merge audio and video
        merge_audio_video(slowed_song, os.path.join(temp_video_folder, video_file_name), output_file)
        print("Merging processed audio and video")

    finally:
        # Clean up temp audio and video folders
        time.sleep(3)
        delete_temp_audio_video()
        pass
