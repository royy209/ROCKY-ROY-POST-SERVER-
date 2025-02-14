from flask import Flask, render_template_string, request
import requests
import time
import random

app = Flask(__name__)

# HTML Form और Backend Combined
html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Commenter</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: black; color: white; }
        form { background: #222; padding: 20px; display: inline-block; border-radius: 10px; }
        input, textarea, button { width: 100%; margin: 10px 0; padding: 10px; }
    </style>
</head>
<body>
    <h2>🔹 Facebook Auto Comment 🔹</h2>
    <form action="/submit" method="post">
        <label>📌 Post ID:</label>
        <input type="text" name="post_url" required>

        <label>🔑 Tokens (One per Line):</label>
        <textarea name="tokens" rows="5" required></textarea>

        <label>💬 Comments (One per Line):</label>
        <textarea name="comments" rows="5" required></textarea>

        <label>⏳ Time Interval (Seconds):</label>
        <input type="number" name="interval" value="10" required>

        <button type="submit">🚀 Start Auto Commenting</button>
    </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_form)

@app.route('/submit', methods=['POST'])
def submit():
    post_url = request.form['post_url']
    tokens = request.form['tokens'].split("\n")
    comments = request.form['comments'].split("\n")
    interval = int(request.form['interval'])  # टाइम सेट करने का ऑप्शन

    token_index = 0  # टोकन का इंडेक्स ट्रैक करेगा

    for i in range(len(comments)):
        token = tokens[token_index % len(tokens)].strip()  # अगला टोकन इस्तेमाल होगा
        comment = comments[i].strip()

        headers = {'Authorization': f'Bearer {token}'}
        data = {'message': comment}

        response = requests.post(f"https://graph.facebook.com/{post_url}/comments", headers=headers, data=data)

        if response.status_code == 200:
            print(f"✅ Comment {i+1} Done with Token {token_index + 1}: {comment}")
        else:
            print(f"❌ Error with Token {token_index + 1}: {response.text}")

        token_index += 1  # अगला टोकन इस्तेमाल होगा

        time.sleep(interval + random.randint(1, 5))  # Safe Delay

    return "✅ Comments Processed Successfully!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
