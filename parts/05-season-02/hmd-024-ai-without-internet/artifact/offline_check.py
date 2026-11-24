"""HMD-024 · is this machine really cut off from the public internet?

Two kinds of probe, each with a short timeout. The machine counts as OFFLINE only if every probe fails:

  DNS   the system resolver looks up two public names, and a raw DNS question (UDP 53) goes straight to public
        resolvers by IP address, two IPv4 and one IPv6 (so a cached answer in the OS cannot fake a pass)
  TCP   a TCP connection to port 443 of public hosts by IP address, two IPv4 and one IPv6 (no DNS needed)

This tests a handful of well-known internet addresses, not "every possible route": a proxy or a VPN that only
lets some traffic through could still exist. It is a strong practical check, not a proof.

Ollama itself listens on 127.0.0.1, so a local model keeps working when all of this fails. What the check tests is
access to the public internet, which is what any cloud AI service needs. It does not test a local or national
network, and it says nothing about security (an offline machine can still leak a file later).

    python3 offline_check.py            # one check
    python3 offline_check.py --watch    # re-check every second; red while online, green once offline (for camera)
"""
import random
import socket
import struct
import sys
import threading
import time

DNS_NAMES = ['example.com', 'wikipedia.org']
DNS_SERVERS = ['1.1.1.1', '8.8.8.8', '2606:4700:4700::1111']           # the last one is IPv6
TCP_HOSTS = [('1.1.1.1', 443), ('9.9.9.9', 443), ('2001:4860:4860::8888', 443)]
TIMEOUT = 2.5


def _with_timeout(fn, timeout):
    box = {}

    def run():
        try:
            box['v'] = fn()
        except Exception as e:  # noqa: BLE001 — any failure means "did not reach the internet"
            box['e'] = e
    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return None, 'timeout'
    return box.get('v'), (type(box['e']).__name__ if 'e' in box else None)


def system_dns(name):
    v, err = _with_timeout(lambda: socket.getaddrinfo(name, 443, proto=socket.IPPROTO_TCP), TIMEOUT)
    return bool(v), err or 'resolved'


def raw_dns(server, name='example.com'):
    """Send one DNS A query over UDP to `server`; True if any reply comes back."""
    qid = random.randrange(65536)
    q = struct.pack('>HHHHHH', qid, 0x0100, 1, 0, 0, 0)
    q += b''.join(bytes([len(p)]) + p.encode() for p in name.split('.')) + b'\0' + struct.pack('>HH', 1, 1)
    try:
        s = socket.socket(socket.AF_INET6 if ':' in server else socket.AF_INET, socket.SOCK_DGRAM)
    except OSError as e:  # no IPv6 stack at all: cannot reach that resolver
        return False, type(e).__name__
    s.settimeout(TIMEOUT)
    try:
        s.sendto(q, (server, 53))
        data, _ = s.recvfrom(512)
        return data[:2] == q[:2], 'answered'
    except Exception as e:  # noqa: BLE001
        return False, type(e).__name__
    finally:
        s.close()


def tcp(host, port):
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return True, 'connected'
    except Exception as e:  # noqa: BLE001
        return False, type(e).__name__


def check(probes=None):
    """Run every probe. `probes` lets the self-test swap in fakes. Returns (offline: bool, rows)."""
    probes = probes or {
        **{f'dns system {n}': (lambda n=n: system_dns(n)) for n in DNS_NAMES},
        **{f'dns raw @{s}': (lambda s=s: raw_dns(s)) for s in DNS_SERVERS},
        **{f'tcp {h}:{p}': (lambda h=h, p=p: tcp(h, p)) for h, p in TCP_HOSTS},
    }
    rows = []
    results = {}
    threads = []
    for name, fn in probes.items():
        def run(name=name, fn=fn):
            results[name] = fn()
        th = threading.Thread(target=run, daemon=True)
        th.start()
        threads.append(th)
    for th in threads:
        th.join(TIMEOUT * 2 + 1)
    for name in probes:
        ok, detail = results.get(name, (False, 'timeout'))
        rows.append({'probe': name, 'reached_internet': bool(ok), 'detail': detail})
    offline = not any(r['reached_internet'] for r in rows)
    return offline, rows


RED, GREEN, DIM, END = '\033[41;97;1m', '\033[42;30;1m', '\033[2m', '\033[0m'


def banner(offline, color=True):
    if offline:
        txt = '  OFFLINE ✓  no DNS, no TCP to the public internet  '
        return (GREEN + txt + END) if color else txt
    txt = '  ONLINE ✗  turn off Wi-Fi first (and unplug the cable)  '
    return (RED + txt + END) if color else txt


def print_check(offline, rows, color=None):
    color = sys.stdout.isatty() if color is None else color
    for r in rows:
        mark = 'reached' if r['reached_internet'] else 'blocked'
        print(f'  {r["probe"]:28} {mark:8} {DIM if color else ""}{r["detail"]}{END if color else ""}')
    print(banner(offline, color))


def watch():
    print('Watching the network. Turn off Wi-Fi now. Ctrl-C to stop.')
    last = None
    try:
        while True:
            offline, rows = check()
            if offline != last:
                print(time.strftime('%H:%M:%S'))
                print_check(offline, rows)
                last = offline
            time.sleep(1)
    except KeyboardInterrupt:
        return 0 if last else 1


if __name__ == '__main__':
    if '--watch' in sys.argv:
        sys.exit(watch())
    off, rows = check()
    print_check(off, rows)
    sys.exit(0 if off else 1)
