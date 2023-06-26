import os
import shutil
import time
import random
from pydub import AudioSegment
from pytube import YouTube
from moviepy.editor import AudioFileClip, concatenate_videoclips, ImageSequenceClip
import numpy as np
from pedalboard import Reverb
from pedalboard.io import AudioFile

audio_folder = "audio_folder"
gif = "gif"
temp_audio_folder = "temp_audio_folder"
temp_video_folder = "temp_video_folder"
final_video_folder = "final_video_folder"

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


def merge_audio_gif(audio_path, gif_paths, output_path):
    audio = AudioFileClip(audio_path)
    gifs = ImageSequenceClip(gif_paths, fps=10)

    video = concatenate_videoclips([gifs] * int(audio.duration / gifs.duration))

    video = video.set_audio(audio)
    # Write the final video with audio
    video.write_videofile(output_path, codec="libx264", audio_codec="libmp3lame", fps=10, preset="ultrafast", bitrate="5000k")



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


# Get the list of audio files in the audio_folder
audio_files = os.listdir(audio_folder)
gif_files = os.listdir(gif)

for audio_file in audio_files:
    # Construct file paths
    song = os.path.splitext(audio_file)[0]
    audio_path = os.path.join(audio_folder, audio_file)
    slowed_song = os.path.join(temp_audio_folder, f"{song} slowed.mp3")
    print (slowed_song)
    output_path = os.path.join(final_video_folder, f"{song} slowed and reverb.mp4")

    random_gif_file = random.choice(gif_files)
    print (random_gif_file)
    gif_path = os.path.join(gif, random_gif_file)
    print (gif_path)

    # Add reverb to the audio
    add_reverb_to_audio(audio_path, slowed_song)
    print("Adding reverb to audio completed:", audio_path)

    try:
        # Merge audio and gif
        merge_audio_gif(slowed_song, [gif_path], output_path)
        print("Merging processed audio and gif")

    finally:
        # Clean up temp audio and video folders
        time.sleep(3)
        delete_temp_audio_video()
        pass
