from flask import Flask, request, render_template_string
import requests, threading, time, random

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64)",
]

EMOJIS = [
    "😂", "😍", "🥰", "😊", "😁", "😉", "😎", "🤩", "😜", "🤪",
    "🤗", "🙃", "😋", "😆", "😝", "😇", "🥳", "🤓", "🧐", "😏",
]

HTML_FORM = '''
<html>
<head><title>Auto Comment Tool</title></head>
<body style="background-color:black; color:white;">
    <h2 style="color:lime;">Facebook Auto Comment Tool</h2>
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

def is_internet_available():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

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
            post_id = post_url.split("/")[-1].split("?")[0]
    except:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    blocked_tokens = set()

    def generate_random_user_agent():
        os = random.choice(["Windows", "Macintosh", "Linux", "Android", "iPhone"])
        version = f"{random.randint(5, 15)}.{random.randint(0, 9)}"
        return f"Mozilla/5.0 ({os}; CPU {os} OS {version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(70, 120)}.0.{random.randint(1000,9999)}.100 Safari/537.36"

    for _ in range(30):
        USER_AGENTS.append(generate_random_user_agent())

    def rotate_user_agent():
        while True:
            time.sleep(1800)
            new_agent = generate_random_user_agent()
            USER_AGENTS.append(new_agent)
            print(f"✅ New User-Agent Added: {new_agent}")

    threading.Thread(target=rotate_user_agent, daemon=True).start()

    def check_blocked_tokens():
        while True:
            time.sleep(300)
            for token in list(blocked_tokens):
                try:
                    r = requests.get(f"https://graph.facebook.com/me?access_token={token}")
                    if r.status_code == 200 and 'id' in r.json():
                        blocked_tokens.remove(token)
                        print(f"♻️ Token re-activated: {token[:10]}...")
                except:
                    pass

    threading.Thread(target=check_blocked_tokens, daemon=True).start()

    def comment_loop():
        comment_index = 0
        round_count = 1
        success_count = 0
        failed_count = 0

        while True:
            if not is_internet_available():
                print("❌ No internet. Retrying in 60s...")
                time.sleep(60)
                continue

            active_tokens = [t for t in tokens if t not in blocked_tokens]
            random.shuffle(active_tokens)

            if not active_tokens:
                print("⏳ All tokens blocked. Waiting 5 mins...")
                time.sleep(300)
                continue

            print(f"\n▶️ Round {round_count}: Each token will comment once")

            for token in active_tokens:
                if not comments:
                    print("⚠️ Comment list is empty!")
                    break

                while not is_internet_available():
                    print("⚠️ Waiting for internet to return...")
                    time.sleep(60)

                comment = comments[comment_index % len(comments)]
                emoji = random.choice(EMOJIS)
                final_comment = f"{emoji} {comment} {emoji}" if random.random() > 0.5 else f"{comment} {emoji}"

                headers = {"User-Agent": random.choice(USER_AGENTS)}
                payload = {'message': final_comment, 'access_token': token}
                comment_url = f"https://graph.facebook.com/{post_id}/comments"

                try:
                    r = requests.post(comment_url, data=payload, headers=headers)
                    if r.status_code == 200:
                        success_count += 1
                        print(f"✅ [{success_count}] {token[:10]}... → {final_comment}")
                    else:
                        failed_count += 1
                        print(f"❌ [{failed_count}] {token[:10]}... → {r.text}")
                        if "OAuthException" in r.text:
                            blocked_tokens.add(token)
                except Exception as e:
                    failed_count += 1
                    print(f"⚠️ [{failed_count}] Error: {e}")
                    blocked_tokens.add(token)

                comment_index += 1
                time.sleep(interval + random.randint(3, 8))

            round_count += 1

    threading.Thread(target=comment_loop, daemon=True).start()

    return render_template_string(HTML_FORM, message="✅ Auto Commenting Started!")

if __name__ == '__main__':
    while True:
        try:
            app.run(host='0.0.0.0', port=10000)
        except Exception as e:
            print(f"❌ Flask crashed: {e}. Restarting in 10s...")
            time.sleep(10)
