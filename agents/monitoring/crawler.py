import httpx, bs4, hashlib, time

def fetch(url: str, selector: str = "body"):
    with httpx.Client(timeout=30.0) as client:
        html = client.get(url).text
    soup = bs4.BeautifulSoup(html, "lxml")
    text = soup.select_one(selector).get_text(" ", strip=True)
    uid = hashlib.md5((url + str(len(text))).encode()).hexdigest()[:10]
    return uid, text[:8000]
