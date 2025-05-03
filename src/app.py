from flask import Flask
import yt_dlp

app = Flask(__name__)

ydl = yt_dlp.YoutubeDL({
    'skip_download': True,
    'dump_single_json': True, # Get the info as a single JSON object
    'extract_flat': True,    # Extract info without resolving formats (faster for just info)
    'verbose': False,        # Set to True to see yt-dlp's internal output
    'logger': None,          # Optional: provide a custom logger if needed
})

@app.route('/')
def hello_world():
    return 'buh'

@app.route('/t/<path:id>')
def redirect_to_target(id):
    """
    Returns an HTML page with a script that redirects to the path
    provided in the URL after /t/.
    """
    global ydl

    try:
        vinfo = ydl.extract_info(f'https://clips.twitch.tv/{id}', download=False)
        video_format = vinfo["formats"][max(3, len(vinfo["formats"]) - 1)]
        width = int(video_format["height"] * video_format["aspect_ratio"])
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Website Name</title>
        <meta content="{vinfo["channel"]}" property="og:title" />
        <meta content="{vinfo["title"]}" property="og:description" />
        <meta content="https://clips.twitch.tv/{id}" property="og:url" />
        <meta content="{video_format["url"]}" property="og:video" />
        <meta content="#43B581" data-react-helmet="true" name="theme-color" />

        <meta property="og:video"
        content="{video_format["url"]}" />
        <meta property="og:video:secure_url"
            content="{video_format["url"]}" />
        <meta property="og:video:height" content="{width}" />
        <meta property="og:video:width" content="{video_format["height"]}" />
        <meta property="og:video:type" content="video/mp4" />
        // <meta property="og:image" content="https://pbs.twimg.com/amplify_video_thumb/1915723648825974784/img/p89_kVK_sfwz8Iat.jpg" />
        <meta property="og:site_name" content="Botge" />
    </head>
    <body>
        <script>
            // Redirect using JavaScript to the target URL
            window.location.replace('https://clips.twitch.tv/{id}');
        </script>
    </body>
    </html>
    """
    # Return the HTML content with the appropriate MIME type
    return html_content

