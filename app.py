from flask import Flask, request, render_template_string
import requests
import time
import random
import threading
import os

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment - Carter by Rocky Roy</title>
    <style>
        body {
            background-color: #111;
            color: white;
            text-align: center;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        input, button {
            width: 90%;
            max-width: 400px;
            padding: 12px;
            margin: 8px;
            border-radius: 8px;
            border: none;
            font-size: 16px;
        }
        button {
            background-color: #28a745;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
        h1 {
            color: #ffcc00;
        }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment - Carter by Rocky Roy</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="file" name="time_file" accept=".txt" required><br>
        <button type="submit">Start Safe Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

blocked_tokens = {}  # Blocked Tokens को ट्रैक करने के लिए

def safe_commenting(tokens, comments, post_id, interval):
    url = f"https://graph.facebook.com/{post_id}/comments"

    def modify_comment(comment):
        emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌", "🎉", "😉", "💪"]
        variations = ["!!", "!!!", "✔️", "...", "🤩", "💥"]
        return f"{random.choice(variations)} {comment} {random.choice(emojis)}"

    token_index = 0
    while True:
        token = tokens[token_index % len(tokens)]

        # **अगर Token Blocked है और Unblock नहीं हुआ, तो Skip करो**
        if token in blocked_tokens and time.time() < blocked_tokens[token]:
            print(f"🚫 Skipping Blocked Token ({token_index+1}), Retrying Later...")
            token_index += 1
            time.sleep(10)
            continue

        comment = comments[token_index % len(comments)]
        response = requests.post(url, data={'message': modify_comment(comment), 'access_token': token})

        if response.status_code == 200:
            print(f"✅ Token {token_index+1} से Comment Success!")
            if token in blocked_tokens:
                del blocked_tokens[token]  # **अगर Token Unblock हो गया तो हटाओ**
        else:
            print(f"❌ Token {token_index+1} Blocked, Trying Again Later...")
            blocked_tokens[token] = time.time() + 600  # **Token 10 Min बाद Try होगा**

        token_index += 1
        safe_delay = interval + random.randint(300, 540)  # **Safe Delay for Anti-Ban**
        print(f"⏳ Waiting {safe_delay} seconds before next comment...")
        time.sleep(safe_delay)

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    time_file = request.files['time_file']
    post_url = request.form['post_url']

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()
    interval = int(time_file.read().decode('utf-8').strip())

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    threading.Thread(target=safe_commenting, args=(tokens, comments, post_id, interval), daemon=True).start()
    return render_template_string(HTML_FORM, message="✅ Commenting Process Started in Background!")

# **Auto Restart Every 15 Min**
def restart_server():
    while True:
        time.sleep(900)  # **15 Min Restart**
        os.system("kill -9 $(lsof -t -i:10000)")
        os.system("python3 app.py")

threading.Thread(target=restart_server, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)
