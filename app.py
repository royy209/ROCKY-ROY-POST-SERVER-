from flask import Flask, request, render_template_string
import requests
import time

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Auto Comment - Created by Raghu ACC Rullx</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Created by Raghu ACC Rullx Boy</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt"><br>
        <input type="file" name="cookies_file" accept=".txt"><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Interval in Seconds (e.g., 300)" required><br>
        <button type="submit">Submit Your Details</button>
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
    token_file = request.files.get('token_file')
    cookies_file = request.files.get('cookies_file')
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    comments = comment_file.read().decode('utf-8').splitlines()
    
    # Extract Post ID from URL
    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"
    success_count = 0

    # Try Token First
    if token_file:
        tokens = token_file.read().decode('utf-8').splitlines()
        for token in tokens:
            for comment in comments:
                payload = {'message': comment, 'access_token': token}
                response = requests.post(url, data=payload)

                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 400:
                    continue  # Invalid token, try next method
                else:
                    continue  # Other errors, skip to next

                time.sleep(interval)

    # If Token Fails, Try Cookies
    if cookies_file:
        cookies = cookies_file.read().decode('utf-8').strip()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookies
        }

        for comment in comments:
            fb_dtsg = "AQG..."  # यहाँ Dynamic fb_dtsg Extract करने का Code जोड़ सकते हो
            data = {
                "fb_dtsg": fb_dtsg,
                "comment_text": comment
            }

            response = requests.post(f"https://www.facebook.com/ufi/add/comment/?post_id={post_id}", headers=headers, data=data)

            if response.status_code == 200:
                success_count += 1
            else:
                continue  # Skip on failure

            time.sleep(interval)

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
