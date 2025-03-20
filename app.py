from flask import Flask, request, render_template_string
import requests
import time
import random
import threading

app = Flask(__name__)

# ✅ **20 Random User-Agents**
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36",
    "Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-J730G) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A505FN) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-J701F) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; SM-G532G) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; SM-J727T) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 10; Mi 9T Pro) AppleWebKit/537.36"
]

# ✅ **HTML Form (Live Console Included)**
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
        #console { background-color: black; color: lime; text-align: left; padding: 10px; height: 300px; overflow-y: auto; border: 1px solid white; }
    </style>
    <script>
        function updateConsole(msg) {
            var consoleDiv = document.getElementById("console");
            consoleDiv.innerHTML += msg + "<br>";
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
        }
    </script>
</head>
<body>
    <h1>Facebook Auto Comment (Advanced)</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="cookie_file" accept=".txt"><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Time Interval in Seconds (e.g., 30)" required><br>
        <button type="submit">Start Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
    <h2>Live Console:</h2>
    <div id="console"></div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    cookie_file = request.files.get('cookie_file')
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()
    cookies = cookie_file.read().decode('utf-8').splitlines() if cookie_file else []

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"

    def post_comment(token, comment, cookie=None):
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }
        payload = {'message': comment, 'access_token': token}

        if cookie:
            headers["Cookie"] = f"c_user={cookie}"

        response = requests.post(url, data=payload, headers=headers)
        return response

    def start_commenting():
        success_count = 0
        while True:
            for i, comment in enumerate(comments):
                token = tokens[i % len(tokens)]
                cookie = cookies[i % len(cookies)] if cookies else None

                random_emojis = ["😊", "🔥", "👍", "💯", "✔️", "🚀"]
                modified_comment = f"{comment} {random.choice(random_emojis)}"

                response = post_comment(token, modified_comment, cookie)

                if response.status_code == 200:
                    success_count += 1
                    log_message = f"✅ Comment Success! ({success_count}) - {modified_comment}"
                else:
                    log_message = f"❌ Failed Comment! - {response.text}"

                print(log_message)
                
                with app.app_context():
                    update_console(log_message)

                time.sleep(interval + random.randint(10, 30))

    def update_console(message):
        with open("console_log.txt", "a") as f:
            f.write(message + "\n")

    comment_thread = threading.Thread(target=start_commenting, daemon=True)
    comment_thread.start()

    return render_template_string(HTML_FORM, message=f"✅ Commenting Started!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
