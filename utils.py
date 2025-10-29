import os, re, time, requests
from urllib.parse import urljoin
from settings import HEADERS, TIMEOUT

def ensure_dir(p: str) -> None:
    if p:
        os.makedirs(p, exist_ok=True)

def slugify(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.strip().lower())
    return re.sub(r"-+", "-", s).strip("-")

def get(url: str, delay: float = 0.0, session: requests.Session | None = None) -> requests.Response:
    s = session or requests.Session()
    r = s.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    if delay:
        time.sleep(delay)
    return r

def download(url: str, out_path: str, delay: float = 0.0, session: requests.Session | None = None) -> None:
    ensure_dir(os.path.dirname(out_path))
    s = session or requests.Session()
    with s.get(url, headers=HEADERS, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
    if delay:
        time.sleep(delay)

def abs_url(base: str, href: str) -> str:
    return urljoin(base, href)
