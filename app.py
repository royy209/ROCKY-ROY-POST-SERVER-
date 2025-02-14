from flask import Flask, request, render_template_string
import requests
import time
import itertools

app = Flask(__name__)

# ✅ HTML फॉर्म
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment - Multi Token & Cookies</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment - Multi Token & Cookies</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt"><br>
        <input type="file" name="cookies_file" accept=".txt"><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Interval in Seconds (e.g., 500)" required><br>
        <button type="submit">Submit</button>
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

    # ✅ Data Reading
    tokens = token_file.read().decode('utf-8').splitlines() if token_file else []
    cookies_list = cookies_file.read().decode('utf-8').splitlines() if cookies_file else []
    comments = comment_file.read().decode('utf-8').splitlines()

    # ✅ Extract Post ID
    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"
    success_count = 0

    # ✅ Loops through Tokens and Cookies One by One
    token_cycle = itertools.cycle(tokens)
    cookies_cycle = itertools.cycle(cookies_list)

    for comment in comments:
        token = next(token_cycle) if tokens else None
        cookies = next(cookies_cycle) if cookies_list else None

        if token:
            payload = {'message': comment, 'access_token': token}
            response = requests.post(url, data=payload)

            if response.status_code == 200:
                success_count += 1
                print(f"✅ Comment Posted with Token: {comment}")
            else:
                print(f"❌ Token Failed, Trying Cookies...")

                if cookies:
                    cookies_dict = dict(item.split("=") for item in cookies.split("; "))
                    comment_url = f"https://www.facebook.com/ufi/add/comment/?dpr=1"

                    headers = {
                        "User-Agent": "Mozilla/5.0",
                        "Referer": f"https://www.facebook.com/{post_id}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }

                    data = {
                        "ft_ent_identifier": post_id,
                        "comment_text": comment
                    }

                    response = requests.post(comment_url, headers=headers, cookies=cookies_dict, data=data)

                    if response.status_code == 200:
                        success_count += 1
                        print(f"✅ Comment Posted with Cookies: {comment}")
                    else:
                        print(f"❌ Cookies भी फेल हो गई!")

        time.sleep(interval)  # ⏳ Delay for next comment

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
