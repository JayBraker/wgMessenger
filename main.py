from bs4 import BeautifulSoup
from wgAuth import wgAuth
import json
import re

MAIL=""
PASSWD=""

auth = wgAuth(MAIL, PASSWD)
sess = auth.session

msgs = sess.get(f"{auth.BASE_URL}/ajax/conversations.php", params={"action": "all-conversations-notifications"}, auth = auth)
assert msgs.ok
body = msgs.json()

unread = [msg for msg in body["_embedded"]["conversations"] if bool(int(msg["unread"]))]
for msg in unread:
    page = sess.get(f"{auth.BASE_URL}/nachricht.html", params={"nachrichten-id": msg['conversation_id']}, auth = auth)
    assert page.ok
    soup = BeautifulSoup(page.text, "html.parser")
    messages = soup.find_all("div", class_="message_content")
    print(messages[-1].text)