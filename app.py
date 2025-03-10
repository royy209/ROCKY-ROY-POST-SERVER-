from flask import Flask, request, render_template_string
import requests
import time
import random

app = Flask(__name__)

# ✅ HTML Form
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
    <h1>🔥 Facebook Auto Comment 🚀</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Time Interval in Seconds (e.g., 30)" required><br>
        <button type="submit">😃 Start Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

# ✅ Emoji List for Safe Commenting
EMOJIS = ["😃", "🔥", "💖", "🚀", "✅", "✨", "🙌", "💯", "😊", "👍", "🥰", "🤩"]

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
    active_tokens = tokens.copy()  # **Active Tokens List**

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"

    def post_comment(token, comment):
        emoji = random.choice(EMOJIS)  # **Random Emoji Add for Anti-Ban**
        payload = {'message': f"{comment} {emoji}", 'access_token': token}
        response = requests.post(url, data=payload)
        return response

    success_count = 0
    failed_tokens = []
    
    # ✅ **हर Token से एक-एक Comment जाएगा, फिर अगला Token यूज़ होगा**
    while comments:
        for token in active_tokens:
            if not comments:
                break  # **अगर Comments खत्म हो गए, तो Loop से बाहर आ जाओ**
                
            comment = comments.pop(0)  # **पहला Comment लो**
            response = post_comment(token, comment)

            if response.status_code == 200:
                success_count += 1
                print(f"✅ Comment Success! Token: {token[:10]}... 🎉")
            else:
                print(f"❌ Token Blocked: {token[:10]} 🚫")
                failed_tokens.append(token)
            
            time.sleep(interval + random.randint(5, 15))  # **Safe Delay for Anti-Ban ⏳**

        # **अगर सारे Tokens Block हो गए तो 10 मिनट Wait करेगा और फिर Try करेगा**
        if len(failed_tokens) == len(active_tokens):
            print("🚫 All Tokens Blocked! Waiting for Unblock...")
            time.sleep(600)  # **10 Min Wait for Token Recovery**
            active_tokens = tokens.copy()  # **Tokens फिर से Try करें**
            failed_tokens = []  # **Blocked Tokens Reset करें**

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Posted! 😃")

if __name__ == '__main__':
    port = 10000  # ✅ **Port Set for Render**
    app.run(host='0.0.0.0', port=port)
