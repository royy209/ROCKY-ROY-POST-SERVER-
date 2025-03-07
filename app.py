from flask import Flask, render_template, request
import requests
import time
import random
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 📌 6 User-Agents for Spoofing
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 15_5 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/109.0.1518.61"
]

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Auto Comment</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #000; color: white; text-align: center; padding: 20px; }
            h2 { color: #00ff00; }
            form { background: #222; padding: 20px; border-radius: 10px; display: inline-block; }
            input, textarea { margin: 10px; padding: 10px; border: none; border-radius: 5px; width: 90%; }
            input[type="submit"] { background-color: #00ff00; color: black; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>✅ Facebook Auto Comment Script</h2>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <label>📂 Upload Token.txt:</label><br>
            <input type="file" name="token_file" required><br>

            <label>📂 Upload Comments.txt:</label><br>
            <input type="file" name="comments_file" required><br>

            <label>🔗 Enter Facebook Post URL:</label><br>
            <input type="text" name="post_url" placeholder="https://facebook.com/yourpost" required><br>

            <label>⏳ Enter Time Interval (seconds):</label><br>
            <input type="number" name="time_interval" placeholder="Enter time in seconds" required><br>

            <input type="submit" value="📤 Upload & Start">
        </form>

        <br><br>
        <a href="/start" style="color: #00ff00; font-size: 20px;">🚀 Start Commenting</a>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # ✅ Save Uploaded Files
        token_file = request.files['token_file']
        comments_file = request.files['comments_file']
        post_url = request.form['post_url']
        time_interval = request.form['time_interval']

        token_path = os.path.join(UPLOAD_FOLDER, "Token.txt")
        comments_path = os.path.join(UPLOAD_FOLDER, "Comments.txt")

        token_file.save(token_path)
        comments_file.save(comments_path)

        # ✅ Save Post URL and Time Interval
        with open(os.path.join(UPLOAD_FOLDER, "PostURL.txt"), "w") as f:
            f.write(post_url)

        with open(os.path.join(UPLOAD_FOLDER, "Time.txt"), "w") as f:
            f.write(time_interval)

        return "✅ Files uploaded successfully! Now start commenting by visiting /start"
    
    except Exception as e:
        return f"❌ Error in Uploading: {str(e)}"

@app.route('/start')
def start_commenting():
    try:
        # 📂 Read Files
        with open(os.path.join(UPLOAD_FOLDER, "Token.txt"), "r") as f:
            tokens = f.read().splitlines()

        with open(os.path.join(UPLOAD_FOLDER, "Comments.txt"), "r") as f:
            comments = f.read().splitlines()

        with open(os.path.join(UPLOAD_FOLDER, "PostURL.txt"), "r") as f:
            post_url = f.read().strip()

        with open(os.path.join(UPLOAD_FOLDER, "Time.txt"), "r") as f:
            interval = int(f.read().strip())

        # ✅ Extract Post ID
        try:
            post_id = post_url.split("posts/")[1].split("/")[0]
        except IndexError:
            return "❌ Invalid Post URL!"

        url = f"https://graph.facebook.com/{post_id}/comments"

        # 🔄 Auto Commenting System
        while True:
            for token in tokens:
                for comment in comments:
                    emoji_comment = comment + " " + random.choice(["😂", "🤣", "😍", "🔥", "💯", "❤️"])
                    headers = {"User-Agent": random.choice(USER_AGENTS)}
                    payload = {'message': emoji_comment, 'access_token': token}

                    response = requests.post(url, data=payload, headers=headers)

                    if response.status_code == 200:
                        print(f"✅ Commented: {emoji_comment}")
                    else:
                        print(f"❌ Failed for Token: {token}. Retrying after {interval} seconds...")

                    time.sleep(interval)  # ⏳ Time Interval
        
        return "✅ Commenting started! Check your Facebook post."

    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
