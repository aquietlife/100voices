"""
- play loud, play slow, play in reverse - nicholas collins
- play back files constantly
- play back faster - with framerate factor
- play back slower - with framerate factor
- play back smaller subsequence of samples
- play back in reverse

References: 
- https://stackoverflow.com/questions/19962413/how-to-reverse-audio-with-pyaudio
- https://coderslegacy.com/python/pyaudio-recording-and-playing-sound/
- https://people.csail.mit.edu/hubert/pyaudio/
- https://code.activestate.com/recipes/578350-platform-independent-white-noise-generator/
"""

import os
import pyaudio
import random
import struct
import sys
import time
import wave

dir_path = "/Users/jo/Desktop/live_diffusion/commonvoice/wav/"

files = [f for f in os.listdir(dir_path) if f.endswith(".wav")]

CHUNK = 1024

rand_draw_reversed_threshold = 2 # set to 0 to turn off, 2 is a good value
rand_draw_subsample_threshold = 8 # set to 0 to turn off, 8 is a good value

framerate_factor_low = 0.7 # set (both) to 1 to turn off
framerate_factor_high = 1.3 # set (both) to 1 to turn off

current_voice = 0
total_voices = 100

white_noise_duration = 5

# instantiate pyaudio and initialize portaudio system resources
p = pyaudio.PyAudio()

while current_voice < total_voices:
    print("current voice: ", current_voice)

    full_file_path = dir_path + random.choice(files)
    print("file path :", full_file_path)

    with wave.open(full_file_path, 'rb') as wf:
        # adjust playback speed in interger format
        framerate_factor = random.uniform(framerate_factor_low, framerate_factor_high)
        print("framerate factor: ", framerate_factor)

        # instantiate pyaudio and initialize portaudio system resources
        # p = pyaudio.PyAudio()

        sample_rate = wf.getframerate()
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        num_frames = wf.getnframes()
        print("num frames: ", num_frames)
        print("sample_rate: ", sample_rate)

        # open stream
        stream = p.open(format=p.get_format_from_width(sample_width), 
                channels=num_channels,
                rate=int(sample_rate * framerate_factor), 
                output=True)
        print("format: ", p.get_format_from_width(sample_width))

        # read the frames 
        frames = wf.readframes(num_frames)
        unpacked_frames = struct.unpack_from("<" + str(num_frames * num_channels) + "h", frames)

        # reverse some percentage of the time
        rand_draw = random.randrange(10)
        print("reverse random draw: ", rand_draw)
        reversed_frames = unpacked_frames[:]
        if rand_draw < rand_draw_reversed_threshold:
            print("reversing frames")
            reversed_frames = unpacked_frames[::-1]

        # pick out only a small part of total frames
        rand_draw = random.randrange(10)
        print("subsample random draw: ", rand_draw)
        if rand_draw < rand_draw_subsample_threshold:
            print("taking subsample")
            start_frame = random.randrange(0, num_frames - 1)
            end_frame = random.randrange(start_frame, num_frames)
            print("start_frame: ", start_frame)
            print("end_frame: ", end_frame)
            num_frames = end_frame - start_frame
            reversed_frames = reversed_frames[start_frame:end_frame]

        # repack the frames
        packed_frames = struct.pack("<" + str(num_frames * num_channels) + "h", *reversed_frames)

        # play back packed frames
        for i in range(0, len(packed_frames), CHUNK):
            stream.write(packed_frames[i:i+CHUNK])
        #close stream
        stream.close()

        # play white noise
        stream=p.open(format=pyaudio.paInt8,channels=1,rate=sample_rate,output=True)
        for n in range(0, int(10 * CHUNK * num_frames/sample_rate * framerate_factor), 1): 
            stream.write(chr(int(random.random()*16)))
        stream.close()

        # increment current_voice
        current_voice += 1

# releae portaudio system resources
p.terminate()
