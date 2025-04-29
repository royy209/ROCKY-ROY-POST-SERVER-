from flask import Flask, request, render_template_string
import requests, threading, time, random

app = Flask(__name__)

# Basic User-Agent List
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

    # ===== Function to generate fake random User-Agents =====
    def generate_random_user_agent():
        os = random.choice(["Windows", "Macintosh", "Linux", "Android", "iPhone"])
        version = f"{random.randint(5, 15)}.{random.randint(0, 9)}"
        return f"Mozilla/5.0 ({os}; CPU {os} OS {version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(70, 120)}.0.{random.randint(1000,9999)}.100 Safari/537.36"

    # ===== Add 20 new random User-Agents at start =====
    for _ in range(20):
        USER_AGENTS.append(generate_random_user_agent())

    # ===== Background thread: add one new random User-Agent every 30 mins =====
    def rotate_user_agent():
        while True:
            time.sleep(1800)  # 30 minutes
            new_agent = generate_random_user_agent()
            USER_AGENTS.append(new_agent)
            print(f"✅ New User-Agent Added: {new_agent}")

    threading.Thread(target=rotate_user_agent, daemon=True).start()

    # ===== Main Commenting Loop =====
    def comment_loop():
        comment_index = 0
        token_index = 0
        user_agent_index = 0
        success_count = 0
        failed_count = 0

        while True:
            active_tokens = [t for t in tokens if t not in blocked_tokens]
            if not active_tokens:
                print("❌ All Tokens Blocked! Stopping...")
                break

            token = active_tokens[token_index % len(active_tokens)]
            comment = comments[comment_index % len(comments)]
            emoji = random.choice(EMOJIS)
            final_comment = f"{comment} {emoji}"

            ua = USER_AGENTS[user_agent_index % len(USER_AGENTS)]
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
                    print(f"✅ [{success_count}] [{token[:10]}...] Comment Sent: {final_comment} | UA: {ua[:50]}...")
                else:
                    failed_count += 1
                    print(f"❌ [{failed_count}] [{token[:10]}...] Failed: {r.text}")
                    if "OAuthException" in r.text:
                        blocked_tokens.add(token)
            except Exception as e:
                failed_count += 1
                print(f"❌ [{failed_count}] [{token[:10]}...] Error: {e}")

            token_index += 1
            comment_index += 1
            user_agent_index += 1

            time.sleep(interval + random.randint(5, 10))

    threading.Thread(target=comment_loop, daemon=True).start()

    return render_template_string(HTML_FORM, message="✅ Commenting Started Successfully!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
