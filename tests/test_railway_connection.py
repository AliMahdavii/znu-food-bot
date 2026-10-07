"""
Layered ZNU connectivity diagnostic. Run INSIDE the Railway container:

    railway run python tests/test_railway_connection.py
    (or temporarily set the Railway start command to this file)

Optional env: PROXY_URL=http://user:pass@host:port  (credentials are masked in logs)
Each layer prints PASS/FAIL so the failing layer is obvious.
"""
import os
import socket
import ssl
import time
from urllib.parse import urlparse

HOST = "student.znu.ac.ir"
URL = f"https://{HOST}/identity/login"
PROXY = os.getenv("PROXY_URL", "").strip()


def mask(p):
    if not p:
        return "none"
    u = urlparse(p)
    return f"{u.scheme}://***@{u.hostname}:{u.port}" if u.username else p


def step(name, fn):
    t = time.time()
    try:
        result = fn()
        print(f"[PASS] {name} ({time.time() - t:.1f}s) {result or ''}")
        return True
    except Exception as e:  # noqa: BLE001 - diagnostic: show everything
        print(
            f"[FAIL] {name} ({time.time() - t:.1f}s) {type(e).__name__}: {e}")
        return False


def egress_ip():
    import requests
    return requests.get("https://api.ipify.org", timeout=10).text


def dns():
    infos = socket.getaddrinfo(HOST, 443, proto=socket.IPPROTO_TCP)
    return sorted({(("IPv6" if i[0] == socket.AF_INET6 else "IPv4"), i[4][0]) for i in infos})


def tcp(family):
    def run():
        infos = socket.getaddrinfo(HOST, 443, family, socket.SOCK_STREAM)
        if not infos:
            raise RuntimeError("no address for this family")
        ip = infos[0][4][0]
        s = socket.socket(family, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            s.connect(infos[0][4])
        finally:
            s.close()
        return f"connected to {ip}:443"
    return run


def tls():
    ctx = ssl.create_default_context()
    with socket.create_connection((HOST, 443), timeout=10) as raw:
        with ctx.wrap_socket(raw, server_hostname=HOST) as s:
            return f"{s.version()} issuer={dict(x[0] for x in s.getpeercert()['issuer']).get('organizationName')}"


def http():
    import requests
    kw = {"proxies": {"https": PROXY, "http": PROXY}} if PROXY else {}
    r = requests.get(URL, timeout=30, allow_redirects=True, **kw)
    return f"status={r.status_code} final={r.url} bytes={len(r.content)}"


def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        opts = {"headless": True}
        if PROXY:
            u = urlparse(PROXY)
            opts["proxy"] = {"server": f"{u.scheme}://{u.hostname}:{u.port}",
                             "username": u.username or "", "password": u.password or ""}
        b = p.chromium.launch(**opts)
        try:
            page = b.new_page()
            page.on("requestfailed", lambda r: print(
                "   requestfailed:", r.url, r.failure))
            page.on("response", lambda r: print(
                "   response:", r.status, r.url))
            page.on("pageerror", lambda e: print("   pageerror:", e))
            resp = page.goto(URL, wait_until="commit", timeout=30000)
            page.wait_for_selector("#username", timeout=30000)
            return f"status={resp.status if resp else None} final={page.url}"
        finally:
            b.close()


if __name__ == "__main__":
    print("=== ZNU NETWORK DIAGNOSTIC ===")
    print("proxy:", mask(PROXY))
    step("Egress IP (where Railway appears to come from)", egress_ip)
    step("DNS", dns)
    step("TCP IPv4 :443", tcp(socket.AF_INET))
    step("TCP IPv6 :443", tcp(socket.AF_INET6))
    step("TLS handshake", tls)
    step("Python HTTPS GET", http)
    step("Chromium -> login page (#username visible)", browser)
    print("=== END DIAGNOSTIC ===")
