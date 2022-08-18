from bs4 import BeautifulSoup
from wgAuth import wgAuth
import dotenv
import json
import re
import os

def get_unread(MAIL, PASSWD):
	print("Using mail", MAIL, "Password", PASSWD)
	auth = wgAuth(MAIL, PASSWD)
	sess = auth.session

	msgs = sess.get(f"{auth.BASE_URL}/ajax/conversations.php", params={"action": "all-conversations-notifications"}, auth = auth)
	assert msgs.ok
	body = msgs.json()

	unread = [msg for msg in body["_embedded"]["conversations"] if bool(int(msg["unread"]))]
	report = []
	for msg in unread:
		page = sess.get(f"{auth.BASE_URL}/nachricht.html", params={"nachrichten-id": msg['conversation_id']}, auth = auth)
		assert page.ok
		soup = BeautifulSoup(page.text, "html.parser")
		if soup.find("a", class_="mini_profile"):
			author = soup.find("a", class_="mini_profile").parent.contents[0].get_text(strip=True)
		else:
			author = "Unbekannt"
		messages = soup.find_all("div", class_="message_content")
			
		report.append({
			"author": author,
			"message": messages[-1].text,
			"received": msg['last_message_timestamp'],
		#	"history": list(map(lambda message: message.text, messages)),
		})
	return report

def send_reports(reports):
	from pydbus import SystemBus
	
	bus = SystemBus()
	signal = bus.get('org.asamk.Signal', f'/org/asamk/Signal/_{SIGNALID}')
	for report in reports:
		message = f"[{report['received']}]\nNeue Nachricht von {report['author']}:\n{report['message']}"
		signal.sendGroupMessage(message, [], [int(byte) for byte in os.getenv("RCPT_GRP").split(',')])

dotenv.load_dotenv()
MAIL=os.getenv("USR_MAIL")
PASSWD=os.getenv("USR_PASSWD")
SIGNALID=os.getenv("SIGNAL_ID")
send_reports(get_unread(MAIL,PASSWD))
