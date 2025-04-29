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
            post_id = post_url.split("/")[-1].split("?")[0]
    except:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    blocked_tokens = set()

    def generate_random_user_agent():
        os = random.choice(["Windows", "Macintosh", "Linux", "Android", "iPhone"])
        version = f"{random.randint(5, 15)}.{random.randint(0, 9)}"
        return f"Mozilla/5.0 ({os}; CPU {os} OS {version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(70, 120)}.0.{random.randint(1000,9999)}.100 Safari/537.36"

    for _ in range(20):
        USER_AGENTS.append(generate_random_user_agent())

    def rotate_user_agent():
        while True:
            time.sleep(1800)
            new_agent = generate_random_user_agent()
            USER_AGENTS.append(new_agent)
            print(f"✅ New User-Agent Added: {new_agent}")

    threading.Thread(target=rotate_user_agent, daemon=True).start()

    # यह फंक्शन ब्लॉक हुए टोकन को हर 10 मिनट में चेक करता है
    def check_blocked_tokens():
        while True:
            time.sleep(600)
            print("♻️ ब्लॉक टोकन को दोबारा चेक किया जा रहा है...")
            for token in list(blocked_tokens):
                test_url = f"https://graph.facebook.com/me?access_token={token}"
                try:
                    r = requests.get(test_url)
                    if r.status_code == 200 and 'id' in r.json():
                        blocked_tokens.remove(token)
                        print(f"✅ टोकन दोबारा एक्टिव: {token[:10]}...")
                except Exception as e:
                    print(f"⚠️ चेक एरर: {e}")

    threading.Thread(target=check_blocked_tokens, daemon=True).start()

    def comment_loop():
        comment_index = 0
        round_count = 1
        success_count = 0
        failed_count = 0

        while True:
            active_tokens = [t for t in tokens if t not in blocked_tokens]

            if not active_tokens:
                print("❌ सभी टोकन ब्लॉक हैं! 10 मिनट बाद फिर से कोशिश होगी...")
                time.sleep(600)
                continue

            print(f"\n🔄 नया राउंड: हर टोकन से {round_count} कमेंट")

            for token in active_tokens:
                for _ in range(round_count):
                    if not comments:
                        print("⚠️ कमेंट लिस्ट खाली है!")
                        break

                    comment = comments[comment_index % len(comments)]
                    emoji = random.choice(EMOJIS)
                    final_comment = f"{comment} {emoji}"

                    ua = random.choice(USER_AGENTS)
                    headers = {"User-Agent": ua}

                    payload = {
                        'message': final_comment,
                        'access_token': token
                    }
                    comment_url = f"https://graph.facebook.com/{post_id}/comments"

                    try:
                        r = requests.post(comment_url, data=payload, headers=headers)
                        if r.status_code == 200:
                            success_count += 1
                            print(f"✅ [{success_count}] {token[:10]}... → {final_comment}")
                        else:
                            failed_count += 1
                            print(f"❌ [{failed_count}] {token[:10]}... → Fail: {r.text}")
                            if "OAuthException" in r.text:
                                blocked_tokens.add(token)
                                break
                    except Exception as e:
                        failed_count += 1
                        print(f"❌ [{failed_count}] {token[:10]}... → Error: {e}")
                        break

                    comment_index += 1
                    time.sleep(interval + random.randint(5, 10))

            round_count += 1

    threading.Thread(target=comment_loop, daemon=True).start()

    return render_template_string(HTML_FORM, message="✅ Auto Commenting चालू हो गया है!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
