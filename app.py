from flask import Flask, request, render_template_string
import requests
import time
import random
import threading

app = Flask(__name__)

# ✅ **HTML Form**
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment (Render + Koyeb)</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="cookie_file" accept=".txt"><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Time Interval in Seconds (e.g., 30)" required><br>
        <button type="submit">Start Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
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

    # ✅ **Extract Post ID**
    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"

    def post_comment(token, comment, cookie=None):
        headers = {"User-Agent": "Mozilla/5.0"}
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

                # ✅ **Randomized Comment for Anti-Spam**
                random_emojis = ["😊", "🔥", "👍", "💯", "✔️", "🚀"]
                modified_comment = f"{comment} {random.choice(random_emojis)}"

                response = post_comment(token, modified_comment, cookie)

                if response.status_code == 200:
                    success_count += 1
                    print(f"✅ Comment Success! ({success_count})")
                else:
                    print(f"❌ Failed Comment! - {response.text}")

                # ✅ **Safe Delay to Avoid Ban**
                time.sleep(interval + random.randint(10, 30))

    # ✅ **Threading to Keep Comments Running**
    comment_thread = threading.Thread(target=start_commenting, daemon=True)
    comment_thread.start()

    return render_template_string(HTML_FORM, message=f"✅ Commenting Started!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
