"""Modulege"""

from flask import Flask
from yt_dlp import YoutubeDL

app = Flask(__name__)

youtube_dl = YoutubeDL(
    {
        "skip_download": True,
        "dump_single_json": True,  # Get the info as a single JSON object
        "extract_flat": True,  # Extract info without resolving formats (faster for just info)
        "verbose": False,  # Set to True to see yt-dlp's internal output
        "logger": None,  # Optional: provide a custom logger if needed
    }
)


@app.route("/")
def redirect_to_base():
    """Base redirect"""
    return "buh"


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

        url = video_format["url"]
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
    <html lang="en">
    <head>
        <meta charset="utf-8">

        <meta content="#43B581" data-react-helmet="true" name="theme-color">
        <meta content="Botge - {channel} - {upload_date_text}\nClipper: {clipper}\nCategory: {category}\nViews: {view_count}" property="og:site_name">
        <meta content="{title}" property="og:title">

        <meta property="og:type" content="video">
        <meta property="og:video" content="{url}">
        <meta property="og:video:type" content="video/mp4">
        <meta property="og:video:secure_url" content="{url}">
        <meta property="og:video:width" content="{width}">
        <meta property="og:video:height" content="{height}">

        <title>{title}</title>
    </head>
    <body>
        <script>
            window.location.replace('https://clips.twitch.tv/{idge}');
        </script>
    </body>
    </html>
    """
    # Return the HTML content with the appropriate MIME type
    return html_content
