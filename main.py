from pytubefix import YouTube
from pytubefix.cli import on_progress

from rich.console import Console
from rich.table import Table

import os, time, subprocess
import ffmpeg

console = Console()

url_4k = input('Enter a youtube url: ')
if url_4k is None:
    url_4k = 'https://www.youtube.com/watch?v=R3GfuzLMPkA'

url_8k = 'https://www.youtube.com/watch?v=6I5nor_880M'


proxies = {
    # 'http': 'http://127.0.0.1:7890', 
    'https': 'http://127.0.0.1:7890'
}

keys = [
    # "_monostate",
    "itag",
    "mime_type",
    "resolution",
    "fps",
    # "codecs",
    # "type",
    # "subtype",
    "video_codec",
    # "audio_codec",
    # "is_otf",
    "bitrate",
    # "_filesize",
    # "_filesize_kb",
    "_filesize_mb",
    # "_filesize_gb",
    # "is_dash",
    # "abr",
    # "_width",
    # "_height",
    # "is_3d",
    # "is_hdr",
    # "is_live",
    # "includes_multiple_audio_tracks",
    # "is_default_audio_track",
    # "audio_track_name",
    "url",
]

table = Table(show_header=True, header_style="bold magenta")
for key in keys:
    table.add_column(key)


# Payload: {
#     serviceIntegrityDimensions: {
#         poToken: "MnQenNfHb5GLBh6kUYK8yaq-UhMBtrpjdlG668nFHu8CpDhsV2aAaU32sIbval9e4KUcX1nsQBbrKasXu0lYmIdhvz6E1ZOnQKGdK6TILzDZ2aqC9UDBx4wMDzIbxSlVpRqaKWa6dnIdxEFeeTHXkBRLhSP77Q=="
#     }
#     context: {
#         client: {
#             visitorData: "CgtpVXNqTE5LZDZONCjknK-6BjIKCgJISxIEGgAgGg%3D%3D"
#         }
#     }
# }

yt = YouTube(url_4k, proxies=proxies, on_progress_callback=on_progress)
# yt = YouTube(url_8k, proxies=proxies, on_progress_callback=on_progress,
#             use_po_token=True)

print(f'\n\nTitle= {yt.title}\n')
title = yt.title

for key in yt.streams[0].__dict__.keys():print(key)

VDO_8K = VDO_4K = VDO_1440P = VDO_1080P = False

for k in ['4320p', '2160p', '1440p', '1080p']:
    hd = yt.streams.filter(res=k).first()
    if hd is None:
        print(f'{k} ❌')
        if k == '4320p': VDO_8K = False
        elif k == '2160p': VDO_4K = False
        elif k == '1440p': VDO_1440P = False
        elif k == '1080p': VDO_1080P = False
    else:
        print(f'{k} ✅ {str(getattr(hd, "_filesize_mb")): >10} MB')
        if k == '4320p': VDO_8K = True
        elif k == '2160p': VDO_4K = True
        elif k == '1440p': VDO_1440P = True
        elif k == '1080p': VDO_1080P = True

for idx, stream in enumerate(yt.streams.order_by('resolution').desc()):
    row = tuple(map(lambda x: str(getattr(stream, x)), keys)) 
    # print(row)
    table.add_row(*row)

console.print(table)

output_dir = './output'
temp_audio = 'temp1.mp3'
temp_video = 'temp1.mp4'
merge_file = '_merge_.mp4'

if os.path.exists(os.path.join(output_dir, f'{yt.title}.mp4')):
    os.remove(os.path.join(output_dir, f'{yt.title}.mp4'))
if os.path.exists(os.path.join(output_dir, temp_audio)):
    os.remove(os.path.join(output_dir, temp_audio))
if os.path.exists(os.path.join(output_dir, temp_video)):
    os.remove(os.path.join(output_dir, temp_video))


print('audio downloading ...')
audio = yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by("abr").desc()
t = time.time()
audio.first().download(output_path=output_dir, filename=temp_audio, max_retries=3)
print(f'done, ETA= {time.time() - t:.8f}s')

if VDO_8K:
    print('8K Video downloading ...')
    video = yt.streams.filter(res='4320p').first()
elif not VDO_8K and VDO_4K:
    print('4K Video downloading ...')
    video = yt.streams.filter(res='2160p').first()
elif not VDO_8K and not VDO_4K and VDO_1440P:
    print('1440P Video downloading ...')
    video = yt.streams.filter(res='1440p').first()
elif not VDO_8K and not VDO_4K and not VDO_1440P and VDO_1080P:
    print('1080P Video downloading ...')
    video = yt.streams.filter(res='1080p').first()
else:
    print('❌ NO HD Video download!')

t = time.time()
video.download(output_path=output_dir, filename=temp_video, max_retries=3)
print(f'done, ETA= {time.time() - t:.8f}s')

probe = ffmpeg.probe(os.path.join(output_dir, temp_video))
# len(probe['streams'])
info = probe['streams'][0]

fps = str(info['r_frame_rate']).split('/')[0]

print('video info:')
print(f'{'fps': >10} = {fps}')
print(f'{'encoder': >10} = {info['codec_long_name']}')
print(f'{'resolution': >10} = {info['width']} x {info['height']}')
print(f'{'ratio': >10} = {info['display_aspect_ratio']}')

# info
# ffmpeg -i temp1.mp4 -i temp1.mp3 -y -r 30 1.mp4
# ffmpeg -i temp1.mp4 -i temp1.mp3 -r 30 -vf yadif,format=yuv420p -force_key_frames "expr:gte(t,n_forced/2)" -c:v libx264 -crf 18 -bf 2 -c:a aac -q:a 1 -ac 2 -ar 48000 -use_editlist 0 -movflags +faststart out.mp4

# cmd = 'ffmpeg -i temp_vid.mp4 -i temp_voice.wav -c:v copy -c:a aac -strict experimental -strftime 1 ' + dt_file_name 
print('mergeing ...')
cmd = (' ').join(['ffmpeg',
                  '-i', os.path.join(output_dir, temp_video),
                  '-i', os.path.join(output_dir, temp_audio),
                  '-r', fps,
                  '-y',
                  os.path.join(output_dir, merge_file)
                  ])

t = time.time()
p = subprocess.Popen(cmd.split(), 
                     stdin=subprocess.PIPE, 
                     # creationflags=subprocess.CREATE_NO_WINDOW
                    )

p.wait()

os.rename(os.path.join(output_dir, merge_file),
          os.path.join(output_dir, f'{yt.title}.mp4'))

if os.path.exists(os.path.join(output_dir, temp_audio)):
    os.remove(os.path.join(output_dir, temp_audio))
if os.path.exists(os.path.join(output_dir, temp_video)):
    os.remove(os.path.join(output_dir, temp_video))

print('done')

