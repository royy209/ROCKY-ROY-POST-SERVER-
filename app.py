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
    <title>Facebook Auto Comment (Cookies Based)</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment (Cookies Based)</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="cookies_file" accept=".txt" required><br>
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
    cookies_file = request.files['cookies_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    cookies_list = cookies_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://mbasic.facebook.com/{post_id}/comments"

    def post_comment(cookies, comment):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Cookie": cookies
        }
        payload = {"comment_text": comment}
        response = requests.post(url, data=payload, headers=headers)
        return response

    success_count = 0
    for i, comment in enumerate(comments):
        cookies = cookies_list[i % len(cookies_list)]  # **हर बार नया Cookies यूज़ होगा**
        
        response = post_comment(cookies, comment)

        if response.status_code == 200:
            success_count += 1
            print(f"✅ Comment Success! Cookies {i+1}")
        else:
            print(f"❌ Cookies {i+1} Blocked!")

        time.sleep(interval + random.randint(5, 15))  # **Safe Delay for Anti-Ban**

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # ✅ Port Set for Hosting
