"""embedserver"""

from os import path, listdir, remove
from html import escape
import subprocess, json
from yt_dlp import YoutubeDL
from flask import Flask, send_from_directory, abort, request
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

FILES_DIR = path.normpath(path.join(app.root_path, "..", "files"))

youtube_dl = YoutubeDL(
    {
        "skip_download": False,
        "dump_single_json": True,  # Get the info as a single JSON object
        "extract_flat": True,  # Extract info without resolving formats (faster for just info)
        "verbose": False,  # Set to True to see yt-dlp's internal output
        "logger": None,  # Optional: provide a custom logger if needed,
        "outtmpl": path.join(FILES_DIR, "%(id)s.%(ext)s"),  # directory set; name uses tokens
    }
)

def get_video_size_ffprobe(path: str):
    path = str(path)
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        path,
    ]
    out = subprocess.check_output(cmd)
    info = json.loads(out)
    stream = info.get("streams", [{}])[0]
    return int(stream.get("width")), int(stream.get("height"))

def clean_files():
    for name in listdir(FILES_DIR):
        try:
            pathge = path.join(FILES_DIR, name)
            remove(pathge)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", flush=True)
            pass

scheduler = BackgroundScheduler()
scheduler.add_job(clean_files, 'cron', minute=0)  # run at minute 0 every hour
scheduler.start()

@app.route("/")
def redirect_to_base():
    """Base redirect"""

    return "buh"

@app.route("/files/<path:filename>")
def redirect_to_files(filename):
    file_path = path.join(FILES_DIR, filename)
    if not path.isfile(file_path):
        abort(404)
        
    # send_from_directory prevents directory traversal
    return send_from_directory(FILES_DIR, filename, as_attachment=False)

@app.route("/t/<path:idge>")
def redirect_to_target(idge):
    """
    Returns an HTML page with a script that redirects to the path
    provided in the URL after /t/.
    """

    try:
        vinfo = youtube_dl.extract_info(
            f"https://clips.twitch.tv/{idge}", download=False
        )
        video_format = vinfo["formats"][len(vinfo["formats"]) - 1]

        url = str(video_format["url"]).replace("&amp;", "&")
        height = video_format["height"]
        width = int(height * video_format["aspect_ratio"])

        title = vinfo["title"]
        view_count = vinfo["view_count"]
        clipper = vinfo["uploader"]
        channel = vinfo["channel"]
        upload_date = vinfo["upload_date"]
        upload_date_text = (
            upload_date[:4] + "-" + upload_date[4:6] + "-" + upload_date[6:8]
        )

        if "categories" in vinfo:
            category = vinfo["categories"][0]
        else:
            category = "N/A"
    except Exception as e:
        print(f"An unexpected error occurred: {e}", flush=True)
        return None

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en" prefix="og: https://ogp.me/ns#">
    <head>
        <title>{title}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="theme-color" content="#43B581">

        <meta name="theme-color" content="#43B581" data-react-helmet="true">
        <meta property="og:site_name" content="{channel} - {upload_date_text}\nClipper: {clipper}\nCategory: {category}\nViews: {view_count}">
        <meta property="og:title" content="{title}">
        <meta property="og:url" content="{url}">

        <meta property="og:type" content="video">
        <meta property="og:video" content="{url}">
        <meta property="og:video:type" content="video/mp4">
        <meta property="og:video:secure_url" content="{url}">
        <meta property="og:video:width" content="{width}">
        <meta property="og:video:height" content="{height}">
        <meta property="og:video:alt" content="{channel} channel - {title} named clip">
    </head>
    <body>
        <script>
            window.location.replace('https://clips.twitch.tv/{idge}');
        </script>
    </body>
    </html>
    """

    return html_content

@app.route("/r/<path:permalink>")
def redirect_to_target2(permalink):
    """
    Returns an HTML page with a script that redirects to the path
    provided in the URL after /r/.
    """

    try:
        reddit_url = f"https://www.reddit.com/{permalink}"
        vinfo = youtube_dl.extract_info(reddit_url, download=True)

        if "url" in vinfo:
            url = vinfo["url"]

            if url.startswith('https://www.twitch.tv/'):
                vinfo2 = youtube_dl.extract_info(url, download=False)

                video_format = vinfo2["formats"][len(vinfo2["formats"]) - 1]
                file_url = str(video_format["url"]).replace("&amp;", "&")
                height = video_format["height"]
                width = int(height * video_format["aspect_ratio"])
            elif url.startswith('https://kick.com/'):
                vinfo2 = youtube_dl.extract_info(url, download=True)

                filepath = f"files/{vinfo2["id"]}.{vinfo2["ext"]}"
                file_url = f"{request.host_url}{filepath}"
                width, height = get_video_size_ffprobe(filepath)
            elif url.startswith('https://youtube.com/clip/'):
                return reddit_url
            else:
                return "undefined"  
        else:
            if "id" in vinfo:
                file_url = f"{request.host_url}files/{vinfo["id"]}.{vinfo["ext"]}"
                height = vinfo["height"]
                width = vinfo["width"]
            else:
                return "undefined"

        title = escape(vinfo["alt_title"])
        ups = vinfo["like_count"]
        uploader = vinfo["uploader"]
        comment_count = vinfo["comment_count"]
        if "upload_date" in vinfo:
            upload_date = vinfo["upload_date"]
            upload_date_text = f" - {(
                upload_date[:4] + "-" + upload_date[4:6] + "-" + upload_date[6:8]
            )}"
        else:
            upload_date_text = ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}", flush=True)
        return None
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en" prefix="og: https://ogp.me/ns#">
    <head>
        <title>{title}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="theme-color" content="#4287f5">

        <meta property="og:site_name" content="LivestreamFail{upload_date_text}\nUploader: {uploader}\nUps: {ups}\nComments: {comment_count}">
        <meta property="og:title" content="{title}">
        <meta property="og:url" content="{reddit_url}">

        <meta property="og:type" content="video">
        <meta property="og:video" content="{file_url}">
        <meta property="og:video:type" content="video/mp4">
        <meta property="og:video:secure_url" content="{file_url}">
        <meta property="og:video:width" content="{width}">
        <meta property="og:video:height" content="{height}">
        <meta property="og:video:alt" content="LivestreamFail - {title}">
    </head>
    <body>
        <script>
            window.location.replace('{reddit_url}');
        </script>
    </body>
    </html>
    """
    
    return html_content
