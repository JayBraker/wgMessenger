from requests.auth import AuthBase
from requests import Request
from requests import Session
from bs4 import BeautifulSoup

class wgAuth(AuthBase):
    BASE_URL="https://www.wg-gesucht.de"

    def __init__(self, email: str, passwd: str):
        sess = Session()

        # Step 1: Get a valid Session ID
        assert sess.get(self.BASE_URL).ok
        assert sess.cookies.get("PHPSESSID")

        # Step 2: POST to /ajax.sessions.php?action=log to fetch Authorization cookies
        login = {
            "login_email_username": email,
            "login_password": passwd,
        }

        assert sess.post(f"{self.BASE_URL}/ajax/sessions.php?action=login", json=login).ok
        self.TOKEN = sess.cookies.get("X-Access-Token")
        self.CLIENTID = sess.cookies.get("X-Client-Id")
        self.REFNO = sess.cookies.get("X-Dev-Ref-No")

        # Validate all necessary Cookies were received/set
        assert self.TOKEN
        assert self.CLIENTID
        assert self.REFNO

        # Step 3: Fetch CSRF token (found as attribute with the logut_button)
        page = sess.get(self.BASE_URL)
        assert page.ok
        soup = BeautifulSoup(page.text, "html.parser")

        info = soup.find('a', class_="logout_button")
        assert info

        self.CSRF_TOKEN = info.get_attribute_list("data-csrf_token")[0]
        assert self.CSRF_TOKEN

        self.USERID = info.get_attribute_list("data-user_id")[0]
        assert self.USERID

        self.session = sess

    def __call__(self, r: Request):
        r.headers["X-Authorization"] = f"Bearer {self.TOKEN}"
        r.headers["X-Client-Id"] = self.CLIENTID
        r.headers["X-Dev-Ref-No"] = self.REFNO
        r.headers["X-User-Id"] = self.USERID
        r.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"
        
        return r