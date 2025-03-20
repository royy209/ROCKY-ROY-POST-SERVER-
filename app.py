from flask import Flask, request, render_template_string
import requests
import time
import random

app = Flask(__name__)

# ✅ **Multi User-Agent List**
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
]

# ✅ **Proxy List (Optional, if needed)**
PROXIES = [
    {"http": "http://proxy1:port", "https": "http://proxy1:port"},
    {"http": "http://proxy2:port", "https": "http://proxy2:port"},
]

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
    <h1>Facebook Auto Comment</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
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
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"

    blocked_tokens = set()  # ✅ **Track Blocked Tokens**
    token_index = 0  # ✅ **Token Sequence**
    user_agent_index = 0  # ✅ **User-Agent Sequence**
    proxy_index = 0  # ✅ **Proxy Rotation**

    while True:
        if token_index >= len(tokens):  # **Reset Token Index**
            token_index = 0
            time.sleep(600)  # ✅ **Wait 10 Minutes Before Retrying Blocked Tokens**

        if len(blocked_tokens) == len(tokens):  # **All Tokens Blocked**
            print("❌ All Tokens Blocked! Retrying in 10 minutes...")
            time.sleep(600)
            blocked_tokens.clear()  # ✅ **Unblock Tokens and Retry**

        token = tokens[token_index]
        if token in blocked_tokens:
            token_index += 1
            continue

        comment = random.choice(comments) + " 😊🔥🚀"  # ✅ **Random Emoji with Comment**
        headers = {"User-Agent": USER_AGENTS[user_agent_index]}  # ✅ **Set User-Agent**
        proxy = PROXIES[proxy_index] if PROXIES else None  # ✅ **Set Proxy (if available)**
        
        payload = {'message': comment, 'access_token': token}

        try:
            response = requests.post(url, data=payload, headers=headers, proxies=proxy)
        except requests.exceptions.RequestException:
            print("⚠️ Proxy Error! Switching Proxy...")
            proxy_index = (proxy_index + 1) % len(PROXIES)
            continue

        if response.status_code == 200:
            print(f"✅ Comment Success! Token {token_index+1}")
        else:
            print(f"❌ Token {token_index+1} Blocked!")
            blocked_tokens.add(token)

        token_index += 1
        user_agent_index = (user_agent_index + 1) % len(USER_AGENTS)  # ✅ **Rotate User-Agent**
        proxy_index = (proxy_index + 1) % len(PROXIES)  # ✅ **Rotate Proxy (if needed)**
        
        # ✅ **Randomized Smart Delay**
        safe_delay = interval + random.randint(5, 15)
        print(f"⏳ Waiting {safe_delay} seconds before next comment...")
        time.sleep(safe_delay)

    return render_template_string(HTML_FORM, message="✅ Comments are being posted continuously!")

if __name__ == '__main__':
    port = 10000  # ✅ **Port Set for Deployment**
    app.run(host='0.0.0.0', port=port)
