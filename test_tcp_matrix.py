"""
TCP reachability matrix. Run INSIDE the Railway container:
    railway run python test_tcp_matrix.py
Read-only: opens TCP connections and closes them. No credentials involved.
"""
import socket
import time

TIMEOUT = 10

# (label, host, port). Hosts that are IP literals skip DNS.
TARGETS = [
    ("ZNU student portal",        "student.znu.ac.ir", 443),
    ("ZNU raw IP :443",           "185.67.12.6",       443),
    ("ZNU raw IP :80",            "185.67.12.6",       80),
    ("ZNU main site",             "znu.ac.ir",         443),
    ("Other .ac.ir (Tehran U)",   "ut.ac.ir",          443),
    ("Other .ac.ir (AUT)",        "aut.ac.ir",         443),
    ("Other .ac.ir (Ferdowsi)",   "um.ac.ir",          443),
    ("Iranian site (Digikala)",   "digikala.com",      443),
    ("Iranian site (Aparat)",     "aparat.com",        443),
    ("Iranian site (Varzesh3)",   "varzesh3.com",      443),
    ("Control (Google)",          "google.com",        443),
]


def classify(exc):
    if isinstance(exc, socket.timeout):
        return "TIMEOUT (packets dropped, no reply)"
    if isinstance(exc, ConnectionRefusedError):
        return "REFUSED (host replied RST: port closed/rejected)"
    if isinstance(exc, ConnectionResetError):
        return "RESET"
    if isinstance(exc, OSError) and exc.errno in (101, 113):
        return f"UNREACHABLE (errno {exc.errno}: no route)"
    return f"{type(exc).__name__}: {exc}"


def test(label, host, port):
    try:
        infos = socket.getaddrinfo(
            host, port, socket.AF_INET, socket.SOCK_STREAM)
    except Exception as e:  # noqa: BLE001
        return f"{label:28} {host}:{port:<4} DNS FAIL  {e}"
    ip = infos[0][4][0]
    t = time.time()
    try:
        with socket.create_connection((ip, port), timeout=TIMEOUT):
            return f"{label:28} {host}:{port:<4} {ip:15} PASS     {time.time() - t:4.1f}s"
    except Exception as e:  # noqa: BLE001
        return f"{label:28} {host}:{port:<4} {ip:15} FAIL     {time.time() - t:4.1f}s  {classify(e)}"


if __name__ == "__main__":
    print("=== TCP MATRIX (IPv4, timeout %ss) ===" % TIMEOUT)
    for t in TARGETS:
        print(test(*t))
    print("--- ZNU repeat x3 (rules out one-off drops) ---")
    for i in range(3):
        print(f"try {i + 1}:",
              test("ZNU student portal", "student.znu.ac.ir", 443))
        time.sleep(2)
    print("=== END ===")
