from flask import Flask, request, render_template_string
import requests, threading, time, random

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)",
    "Mozilla/5.0 (Linux; Android 11; Mi 10)",
    "Mozilla/5.0 (Windows NT 10.0; rv:91.0)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPad; CPU OS 14_2)",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)",
    "Mozilla/5.0 (Linux; Android 8.1.0)",
    "Mozilla/5.0 (Windows NT 5.1)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-G973F)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)",
    "Mozilla/5.0 (Macintosh; PPC Mac OS X)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; rv:78.0)",
    "Mozilla/5.0 (Linux; Android 10; Nokia 7.2)"
]

EMOJIS = [
    "😂", "😍", "🥰", "😊", "😁", "😉", "😎", "🤩", "😜", "🤪",
    "🤗", "🙃", "😋", "😆", "😝", "😇", "🥳", "🤓", "🧐", "😏",
    "😅", "😃", "😄", "😺", "😸", "😻", "😽", "🙀", "🐱", "🐯"
]

HTML_FORM = '''
<html>
<head><title>Raghu Auto Comment Tool</title></head>
<body style="background-color:black; color:white;">
    <h2 style="color:lime;">Created by Raghu ACC Rullx Boy</h2>
    <form action="/submit" method="post" enctype="multipart/form-data">
        Token File (.txt): <input type="file" name="token_file" required><br><br>
        Comment File (.txt): <input type="file" name="comment_file" required><br><br>
        Facebook Post URL: <input type="text" name="post_url" required><br><br>
        Interval (Seconds): <input type="number" name="interval" value="400" required><br><br>
        <input type="submit" value="Start Commenting"><br><br>
    </form>
    {% if message %}
        <p style="color:yellow;">{{ message }}</p>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    tokens = request.files['token_file'].read().decode().splitlines()
    comments = request.files['comment_file'].read().decode().splitlines()
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    try:
        if "posts/" in post_url:
            post_id = post_url.split("posts/")[1].split("/")[0]
        elif "permalink/" in post_url:
            post_id = post_url.split("permalink/")[1].split("/")[0]
        else:
            post_id = post_url.split("/")[-1].split("?")[0]  # try last part
    except:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    blocked_tokens = set()
    user_agent_index = [0]

    def rotate_user_agent():
        while True:
            time.sleep(1800)
            new_agent = "Mozilla/5.0 (Random Agent/" + str(random.randint(1000,9999)) + ")"
            USER_AGENTS.append(new_agent)
            print(f"✅ New User-Agent Added: {new_agent}")

    threading.Thread(target=rotate_user_agent, daemon=True).start()

    def comment_loop():
        while True:
            active_tokens = [t for t in tokens if t not in blocked_tokens]
            if not active_tokens:
                print("❌ All Tokens Blocked!")
                break

            for i in range(len(active_tokens)):
                token = active_tokens[i]
                comment = comments[i % len(comments)]
                emoji = random.choice(EMOJIS)
                final_comment = f"{comment} {emoji}"

                ua = USER_AGENTS[user_agent_index[0] % len(USER_AGENTS)]
                user_agent_index[0] += 1

                headers = {"User-Agent": ua}
                comment_payload = {'message': final_comment, 'access_token': token}
                comment_url = f"https://graph.facebook.com/{post_id}/comments"

                try:
                    r = requests.post(comment_url, data=comment_payload, headers=headers)
                    if r.status_code == 200:
                        print(f"✅ Comment Done: {final_comment}")
                    else:
                        print(f"❌ Comment Failed: {r.text}")
                        if "OAuthException" in r.text:
                            blocked_tokens.add(token)
                except Exception as e:
                    print(f"❌ Error in Commenting: {e}")

                time.sleep(interval + random.randint(5, 20))

    threading.Thread(target=comment_loop, daemon=True).start()
    return render_template_string(HTML_FORM, message="✅ Commenting Started Successfully!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
