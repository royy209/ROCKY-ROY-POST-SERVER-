from flask import Flask, request, render_template_string
import requests, threading, time, random

app = Flask(__name__)

USER_AGENTS = [  # 20 Random User Agents
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

HTML_FORM = '''
<html>
<head><title>Raghu Auto Tool</title></head>
<body style="background-color:black; color:white;">
    <h2 style="color:lime;">Created by Raghu ACC Rullx Boy</h2>
    <form action="/submit" method="post" enctype="multipart/form-data">
        Token File: <input type="file" name="token_file" required><br><br>
        Comment File: <input type="file" name="comment_file" required><br><br>
        Message File: <input type="file" name="message_file" required><br><br>
        Cookies File (Optional): <input type="file" name="cookies_file"><br><br>
        Facebook Post URL: <input type="text" name="post_url" required><br><br>
        Receiver ID / Group ID: <input type="text" name="receiver_id" required><br><br>
        Interval (Seconds): <input type="number" name="interval" value="400" required><br><br>
        <input type="submit" value="Start Tool"><br><br>
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
    messages = request.files['message_file'].read().decode().splitlines()
    post_url = request.form['post_url']
    receiver_id = request.form['receiver_id']
    interval = int(request.form['interval'])
    cookies = []

    if 'cookies_file' in request.files and request.files['cookies_file'].filename:
        cookies = request.files['cookies_file'].read().decode().splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    blocked_tokens = set()
    user_agent_index = [0]

    def rotate_user_agent():
        while True:
            time.sleep(1800)
            new_agent = "Mozilla/5.0 (Random Added/" + str(random.randint(1000,9999)) + ")"
            USER_AGENTS.append(new_agent)
            print(f"✅ New User-Agent Added: {new_agent}")

    threading.Thread(target=rotate_user_agent, daemon=True).start()

    def comment_and_message_loop():
        count = 0
        while True:
            active_tokens = [t for t in tokens if t not in blocked_tokens]
            if not active_tokens:
                print("❌ All Tokens Blocked!")
                break

            for i in range(len(active_tokens)):
                token = active_tokens[i]
                comment = comments[i % len(comments)]
                message = messages[i % len(messages)]
                ua = USER_AGENTS[user_agent_index[0] % len(USER_AGENTS)]
                user_agent_index[0] += 1

                headers = {"User-Agent": ua}
                comment_payload = {'message': comment, 'access_token': token}
                comment_url = f"https://graph.facebook.com/{post_id}/comments"

                try:
                    r1 = requests.post(comment_url, data=comment_payload, headers=headers)
                    if r1.status_code == 200:
                        print(f"✅ Comment Done: {comment}")
                    else:
                        print(f"❌ Comment Failed: {r1.text}")
                        if "OAuthException" in r1.text:
                            blocked_tokens.add(token)
                            continue
                except Exception as e:
                    print(f"❌ Error in Commenting: {e}")

                msg_payload = {'message': message, 'access_token': token}
                msg_url = f"https://graph.facebook.com/{receiver_id}/messages"

                try:
                    r2 = requests.post(msg_url, data=msg_payload, headers=headers)
                    if r2.status_code == 200:
                        print(f"✅ Message Sent: {message}")
                    else:
                        print(f"❌ Message Failed: {r2.text}")
                        if "OAuthException" in r2.text:
                            blocked_tokens.add(token)
                except Exception as e:
                    print(f"❌ Error in Messaging: {e}")

                time.sleep(interval + random.randint(5, 25))

    threading.Thread(target=comment_and_message_loop, daemon=True).start()
    return render_template_string(HTML_FORM, message="✅ Tool Started Successfully!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
