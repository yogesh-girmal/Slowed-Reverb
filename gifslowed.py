import os
import shutil
import time
import random
from pydub import AudioSegment
from pytube import YouTube
from moviepy.editor import AudioFileClip, concatenate_videoclips, ImageSequenceClip, VideoFileClip
import numpy as np
from pedalboard import Reverb, Chorus
from pedalboard.io import AudioFile

audio_folder = "audio_folder"
vinyl = "vinyl/vinyl.mp3"
gif = "gif"
temp_audio_folder = "temp_audio_folder"
temp_video_folder = "temp_video_folder"
final_video_folder = "final_video_folder"


def add_reverb_to_audio(infile, outfile):
    # Load the audio file
    audio = AudioSegment.from_file(infile)
    vinyl_clip = AudioSegment.from_file(vinyl)

    audio_with_vinyl = audio.overlay(vinyl_clip, loop=True)

    slow_factor = 0.9
    slow_audio = audio_with_vinyl._spawn(audio_with_vinyl.raw_data, overrides={
        "frame_rate": int(audio_with_vinyl.frame_rate * slow_factor)
    })

    # Convert slow_audio to a numpy array
    audio_array = np.array(slow_audio.get_array_of_samples(), dtype=np.float32) / 32768.0

    chorus = Chorus(rate_hz=0.4, depth=0.1, centre_delay_ms=0.3, feedback=0.5, mix=0.2)

    # Apply the chorus effect to the audio
    chorus_audio = chorus(audio_array, slow_audio.frame_rate)

    reverb = Reverb(room_size=0.3, damping=0.3, wet_level=0.5, dry_level=0.3, width=0.6, freeze_mode= 0.3)

    effect_array = reverb(chorus_audio, slow_audio.frame_rate)

    effect_audio = slow_audio._spawn((effect_array * 32768.0).astype(np.int16))

    effect_audio.export(outfile, format='mp3')



def merge_audio_gif(audio_path, gif_paths, output_path):
    audio = AudioFileClip(audio_path)
    gifs = VideoFileClip(gif_paths)

    video = concatenate_videoclips([gifs] * int(audio.duration / gifs.duration))

    video = video.set_audio(audio)
    # Write the final video with audio
    video.write_videofile(output_path, verbose=False, logger=None)



def create_folders():
    os.makedirs(temp_video_folder, exist_ok=True)
    os.makedirs(final_video_folder, exist_ok=True)

def delete_temp_audio_video():
    # shutil.rmtree(temp_audio_folder)
    # Add a delay before deleting the temp_video_folder to ensure the video file is closed properly
    time.sleep(1)
    #shutil.rmtree(temp_video_folder)

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
        merge_audio_gif(slowed_song, gif_path, output_path)
        print("Merging processed audio and gif")

    finally:
        # Clean up temp audio and video folders
        time.sleep(3)
        delete_temp_audio_video()
        pass
