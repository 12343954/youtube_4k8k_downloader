from pytubefix import YouTube
from pytubefix.cli import on_progress

from rich.console import Console
from rich.table import Table

import os, time, subprocess
import ffmpeg
    
console = Console()

def PrintOK(text):
    console.log(f"[green]{text}")
def PrintInfo(text):
    console.log(f"[blue]{text}")
def PrintWarning(text):
    console.log(text, style="#EE9427")
def PrintRule(text):
    console.rule(f"[bold blue]{text}")
    
console.print("[blue]Github URL: [green]https://github.com/12343954/youtube_4k8k_downloader")
print('')

# https://www.youtube.com/watch?v=tUjIwYeVlQc
url_4k = input('Enter a youtube url (prefer 4K or 8K): ')
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

# Info(f'\n\nTitle= {yt.title}\n')
# title = yt.title

table = Table(show_header=True, header_style="bold magenta")
table.add_column("Title", style="magenta")
table.add_row(yt.title)
console.print(table)
time.sleep(3)

# for key in yt.streams[0].__dict__.keys():print(key)
# time.sleep(3)

VDO_8K = VDO_4K = VDO_1440P = VDO_1080P = False
RESOLUTIONS = [{"label":"8K", "resv":"4320p", "size":"0"},
               {"label":"4K", "resv":"2160p", "size":"0"},
               {"label":"2.5K", "resv":"1440p", "size":"0"},
               {"label":"2K", "resv":"1080p", "size":"0"}]

# Resolutions = ['4320p', '2160p', '1440p', '1080p']
for i, k in enumerate(RESOLUTIONS):
    hd = yt.streams.filter(res=k["resv"]).first()
    if hd is None:
        # Warning(f'{k} ❌')
        if k["resv"] == RESOLUTIONS[0]["resv"]: VDO_8K = False
        elif k["resv"] == RESOLUTIONS[1]["resv"]: VDO_4K = False
        elif k["resv"] == RESOLUTIONS[2]["resv"]: VDO_1440P = False
        elif k["resv"] == RESOLUTIONS[3]["resv"]: VDO_1080P = False
    else:
        # Info(f'{k} ✅ {str(getattr(hd, "_filesize_mb")): >10} MB')
        RESOLUTIONS[i]["size"] = str(getattr(hd, "_filesize_mb"))
        if k["resv"] == RESOLUTIONS[0]["resv"]: VDO_8K = True
        elif k["resv"] == RESOLUTIONS[1]["resv"]: VDO_4K = True
        elif k["resv"] == RESOLUTIONS[2]["resv"]: VDO_1440P = True
        elif k["resv"] == RESOLUTIONS[3]["resv"]: VDO_1080P = True
        
table = Table(show_header=True, header_style="bold magenta")
# table.add_column(["8K", "4K", "2.5K", "2K"])
# table.add_row(*Resolutions)
# table.add_row(*['✅' if VDO_8K else '❌',
#                 '✅' if VDO_4K else '❌',
#                 '✅' if VDO_1440P else '❌',
#                 '✅' if VDO_1080P else '❌',])

for col in list(map(lambda x: f'{x["label"]}/{x["resv"]}', RESOLUTIONS)):
    table.add_column(col)
    
# table.add_row(*list(map(lambda x: x["resv"], RESOLUTIONS)))
table.add_row(*list(map(lambda x: "❌" if x["size"] == "0" else f"✅ {x["size"]} MB", RESOLUTIONS)))
console.print(table)
time.sleep(3)

table = Table(show_header=True, header_style="bold magenta")
for key in keys:
    table.add_column(key)
    
for idx, stream in enumerate(yt.streams.order_by('resolution').desc()):
    row = tuple(map(lambda x: str(getattr(stream, x)), keys)) 
    # print(row)
    table.add_row(*row)

console.print(table)
time.sleep(6)

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


PrintInfo('audio downloading ...')
audio = yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by("abr").desc()
t = time.time()
audio.first().download(output_path=output_dir, filename=temp_audio, max_retries=3)
PrintOK(f'Done, ETA= {time.time() - t:.8f}s')

if VDO_8K:
    PrintInfo('8K Video downloading ...')
    video = yt.streams.filter(res='4320p').first()
elif not VDO_8K and VDO_4K:
    PrintInfo('4K Video downloading ...')
    video = yt.streams.filter(res='2160p').first()
elif not VDO_8K and not VDO_4K and VDO_1440P:
    PrintInfo('1440P Video downloading ...')
    video = yt.streams.filter(res='1440p').first()
elif not VDO_8K and not VDO_4K and not VDO_1440P and VDO_1080P:
    PrintInfo('1080P Video downloading ...')
    video = yt.streams.filter(res='1080p').first()
else:
    PrintWarning('❌ NO HD Video download!')

t = time.time()
video.download(output_path=output_dir, filename=temp_video, max_retries=3)
PrintOK(f'Done, ETA= {time.time() - t:.8f}s')

probe = ffmpeg.probe(os.path.join(output_dir, temp_video))
info = probe['streams'][0]

fps = str(info['r_frame_rate']).split('/')[0]
# or
# fps = str(getattr(video, "fps"))

table = Table(show_header=True, header_style="bold magenta", title="Media Information")
table.add_column("FPS", style="magenta")
table.add_column("Encoder", style="magenta")
table.add_column("Resolution", style="magenta")
table.add_column("Ratio", style="magenta")
table.add_row(fps, info['codec_long_name'], f'{info['width']} x {info['height']}', info['display_aspect_ratio'])
console.print(table)
time.sleep(3)
# OK('video info:')
# Info(f'{'fps': >10} = {fps}')
# Info(f'{'encoder': >10} = {info['codec_long_name']}')
# Info(f'{'resolution': >10} = {info['width']} x {info['height']}')
# Info(f'{'ratio': >10} = {info['display_aspect_ratio']}')

# info
# ffmpeg -i temp1.mp4 -i temp1.mp3 -y -r 30 1.mp4
# ffmpeg -i temp1.mp4 -i temp1.mp3 -r 30 -vf yadif,format=yuv420p -force_key_frames "expr:gte(t,n_forced/2)" -c:v libx264 -crf 18 -bf 2 -c:a aac -q:a 1 -ac 2 -ar 48000 -use_editlist 0 -movflags +faststart out.mp4

# cmd = 'ffmpeg -i temp_vid.mp4 -i temp_voice.wav -c:v copy -c:a aac -strict experimental -strftime 1 ' + dt_file_name 
PrintInfo('mergeing ...')
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

PrintOK('All Done !!!')

