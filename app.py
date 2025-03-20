from flask import Flask, request, render_template_string
import requests
import time
import random
import threading

app = Flask(__name__)

# ✅ **Random User-Agents**
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36"
]

# ✅ **HTML Form**
HTML_FORM = '''
<html>
    <head>
        <title>Facebook Auto Comment</title>
    </head>
    <body>
        <h2>Facebook Auto Comment (Multi-Token Handling)</h2>
        <form action="/submit" method="post" enctype="multipart/form-data">
            Token File: <input type="file" name="token_file" required><br>
            Comment File: <input type="file" name="comment_file" required><br>
            Post URL: <input type="text" name="post_url" required><br>
            Interval (Seconds): <input type="number" name="interval" value="400" required><br>
            <input type="submit" value="Start Commenting">
        </form>
        <br>
        {% if message %}
            <p>{{ message }}</p>
        {% endif %}
    </body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    if not tokens or not comments:
        return render_template_string(HTML_FORM, message="❌ Token या Comment File खाली है!")

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"
    blocked_tokens = set()

    def post_comment(token, comment):
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        payload = {'message': comment, 'access_token': token}

        response = requests.post(url, data=payload, headers=headers)
        
        if response.status_code == 200:
            return True, f"✅ Comment Success - {comment}"
        elif "error" in response.json() and "OAuthException" in response.text:
            blocked_tokens.add(token)  # Blocked Token को List में Add कर दो
            return False, f"❌ Token Blocked! Skipping... ({token[:10]}...)"
        else:
            return False, f"❌ Failed - {response.text}"

    def start_commenting():
        success_count = 0
        while True:
            active_tokens = [t for t in tokens if t not in blocked_tokens]
            if not active_tokens:
                print("❌ All Tokens Blocked! Stopping script.")
                break  # अगर सारे Tokens Block हो जाएँ, तो स्क्रिप्ट बंद हो जाएगी।

            for i, comment in enumerate(comments):
                token = active_tokens[i % len(active_tokens)]  # हर बार नया Token चुनो
                
                # ✅ Comment में Random Emojis Add करो
                random_emojis = ["😊", "🔥", "👍", "💯", "✔️", "🚀"]
                modified_comment = f"{comment} {random.choice(random_emojis)}"

                success, log_message = post_comment(token, modified_comment)

                if success:
                    success_count += 1
                    print(f"✅ Success ({success_count}): {modified_comment}")
                else:
                    print(log_message)

                time.sleep(interval + random.randint(10, 30))  # ✅ Random Delay Add किया

    comment_thread = threading.Thread(target=start_commenting, daemon=True)
    comment_thread.start()

    return render_template_string(HTML_FORM, message="✅ Commenting Started!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
