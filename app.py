import requests
import time

# 🔹 Facebook Post ID & Comment Text
POST_ID = "pfbid02aWuPV16Xqn7SpcwebC1jFNUYpESeaFvXxnajjUccokkDinvU1C5ar35oEcAt3erol"
COMMENT_TEXT = "SAMART X3 YASH HERE :-P"

# 🔹 Facebook Cookies (Update with valid cookies)
COOKIES = {
    "c_user": "100050801325177",
    "fr": "0JGTokJ9AZoyrm3JK.AWUvXfj21f_JgI9F2Xd0e8n2iFIWmP85ac0FCA.BnrKhO..AAA.0.0.BnrLpn.AWXjD7JW4Ds",
    "xs": "25:xxM0FQQMihxoqg:2:1739373161:-1:13215",
    "locale": "en_GB"
}

# 🔹 fb_dtsg Token (Get from Network Tab in Dev Tools)
FB_DTSG = "अपना_fb_dtsg_डालो"  

# 🔹 Comment Function
def post_comment():
    url = f"https://m.facebook.com/{POST_ID}/comments"
    data = {
        "comment_text": COMMENT_TEXT,
        "fb_dtsg": FB_DTSG
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)"
    }
    
    response = requests.post(url, headers=headers, cookies=COOKIES, data=data)
    
    if response.status_code == 200:
        print(f"✅ Comment Successfully Posted on {POST_ID}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")  # Debugging Logs

# 🔹 Infinite Loop (400s Delay Between Comments)
while True:
    post_comment()
    print("⏳ Waiting 400 Seconds for Next Comment...")
    time.sleep(400)  # 400 Seconds Delay
