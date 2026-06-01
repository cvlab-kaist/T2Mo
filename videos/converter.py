from pathlib import Path
from fractions import Fraction
import json
import subprocess


def ffprobe_video_info(path: str):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,r_frame_rate",
        "-of", "json",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    stream = json.loads(result.stdout)["streams"][0]

    width = int(stream["width"])
    height = int(stream["height"])

    rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "30/1"
    try:
        fps = float(Fraction(rate))
        if fps <= 0:
            fps = 30
    except Exception:
        fps = 30

    return width, height, fps


def webm_to_mp4_white_background(input_webm: str, output_mp4: str):
    input_webm = str(Path(input_webm))
    output_mp4 = str(Path(output_mp4))

    width, height, fps = ffprobe_video_info(input_webm)

    cmd = [
        "ffmpeg",
        "-y",

        # Critical: force VP9 decoder that can expose alpha.
        "-c:v", "libvpx-vp9",
        "-i", input_webm,

        "-filter_complex",
        (
            f"color=white:s={width}x{height}:r={fps}[bg];"
            "[0:v]format=yuva420p[fg];"
            "[bg][fg]overlay=shortest=1:format=auto,"
            "format=yuv420p[v]"
        ),

        "-map", "[v]",
        "-map", "0:a?",

        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",

        "-c:a", "aac",
        "-b:a", "192k",

        "-movflags", "+faststart",
        output_mp4,
    ]

    subprocess.run(cmd, check=True)


# webm_to_mp4_white_background("input.webm", "output.mp4")

# Example
from pathlib import Path
from fractions import Fraction
import json
import subprocess


def ffprobe_video_info(path: str):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,r_frame_rate,codec_name,pix_fmt",
        "-of", "json",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    stream = json.loads(result.stdout)["streams"][0]

    width = int(stream["width"])
    height = int(stream["height"])

    rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "30/1"
    try:
        fps = float(Fraction(rate))
        if fps <= 0:
            fps = 30.0
    except Exception:
        fps = 30.0

    return width, height, fps, stream.get("codec_name"), stream.get("pix_fmt")


def mov_to_mp4_white_background(input_mov: str, output_mp4: str):
    input_mov = str(Path(input_mov))
    output_mp4 = str(Path(output_mp4))

    width, height, fps, codec, pix_fmt = ffprobe_video_info(input_mov)

    print(f"Input codec: {codec}")
    print(f"Input pixel format: {pix_fmt}")

    cmd = [
        "ffmpeg",
        "-y",

        # Important: do NOT force libvpx-vp9 here.
        "-i", input_mov,

        "-filter_complex",
        (
            f"color=c=white:s={width}x{height}:r={fps},format=rgba[bg];"
            "[0:v]format=rgba[fg];"
            "[bg][fg]overlay=shortest=1:format=auto,"
            "format=yuv420p[v]"
        ),

        "-map", "[v]",
        "-map", "0:a?",

        # Output encoder
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",

        "-c:a", "aac",
        "-b:a", "192k",

        "-movflags", "+faststart",
        output_mp4,
    ]

    subprocess.run(cmd, check=True)


mov_to_mp4_white_background(
    "/Users/jaeyeong/Downloads/moose_trot_transp_azi210_e-15.mov",
    "/Users/jaeyeong/Desktop/project/T2Mo/Quals/project_page_assets/videos/gallery/moose-trot/video.mp4",
)

# webm_to_mp4_white_background("/Users/jaeyeong/Downloads/moose_trot_transp_azi210_e-15.mov", 
#                              "/Users/jaeyeong/Desktop/project/T2Mo/Quals/project_page_assets/videos/gallery/moose-trot/video.mp4")
