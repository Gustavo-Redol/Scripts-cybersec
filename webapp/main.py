from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"

TOOLS = [
    {
        "name": "Enumeratorinator",
        "file": "Enumeratorinator.sh",
        "language": "bash",
        "category": "Recon",
        "description": "All-in-one reconnaissance: full-port nmap scan, detailed service detection, gobuster directory and DNS subdomain enumeration, directory-listing checks, and /etc/hosts sync for discovered subdomains.",
        "dependencies": ["nmap", "gobuster", "curl", "sudo", "gnome-terminal", "wordlists (dirb, seclists)"],
        "usage": "./Enumeratorinator.sh",
        "notes": "Interactive; prompts for target IP and domain. Saves results to nmap_*.txt and gobuster_*.txt.",
    },
    {
        "name": "Metanalyzer",
        "file": "Metanalyzer.sh",
        "language": "bash",
        "category": "OSINT",
        "description": "Google-dork driven metadata analyzer: searches a target for downloadable documents of a given type, downloads them, and extracts metadata with exiftool.",
        "dependencies": ["lynx", "wget", "exiftool"],
        "usage": "./Metanalyzer.sh",
        "notes": "Interactive; prompts for target URL and one file type (PDF, DOC, DOCX...).",
    },
    {
        "name": "Dir Yandere",
        "file": "diryandere.sh",
        "language": "bash",
        "category": "Web",
        "description": "Automated directory discovery: iterates a wordlist (custom or built-in lista1.txt) and reports paths that return HTTP 200.",
        "dependencies": ["curl", "figlet", "wordlist (lista1.txt or custom)"],
        "usage": "./diryandere.sh",
        "notes": "Interactive; prompts for target URL and optional custom wordlist path.",
    },
    {
        "name": "Email Validador",
        "file": "email-validador.py",
        "language": "python",
        "category": "Web",
        "description": "Async email enumeration against login endpoints: posts candidate emails from a wordlist and flags those whose error responses differ from the 'email does not exist' invalid-state message.",
        "dependencies": ["python3", "aiohttp"],
        "usage": "python3 email-validador.py",
        "notes": "Interactive; prompts for target URL, wordlist and concurrency (default 50). Saves hits to valid_emails.txt.",
    },
    {
        "name": "EternalScaner",
        "file": "eternalscaner.py",
        "language": "python",
        "category": "OSINT",
        "description": "Shodan-powered scanner that queries for Windows hosts with SMB (port 445) exposed and writes the results to eternalblue_vuln.txt.",
        "dependencies": ["python3", "shodan", "SHODAN_API_KEY"],
        "usage": "python3 eternalscaner.py",
        "notes": "Requires a Shodan API key set in the script before running.",
    },
    {
        "name": "Port Pinger",
        "file": "portpinger",
        "language": "bash",
        "category": "Network",
        "description": "TCP port probe using hping3 SYN packets, with an optional callback fetch against a listener port and a summary of the retrieved page.",
        "dependencies": ["hping3", "wget", "sudo"],
        "usage": "./portpinger",
        "notes": "Interactive; prompts for target IPs, port list, and optional callback port.",
    },
    {
        "name": "SYN Flood",
        "file": "synflood_final.c",
        "language": "c",
        "category": "Network",
        "description": "Multi-threaded SYN flood tool built on raw sockets with spoofed source IPs, configurable port, thread count and inter-packet delay.",
        "dependencies": ["gcc", "libpthread", "raw socket / root privileges"],
        "usage": "gcc synflood_final.c -o synflood -lpthread && sudo ./synflood <target_ip> <port> <threads> <delay_us>",
        "notes": "Compile before use; requires root to open raw sockets.",
    },
    {
        "name": "Tomcat Scaner",
        "file": "tomcatscaner.py",
        "language": "python",
        "category": "OSINT",
        "description": "Shodan-powered discovery of Apache Tomcat servers with WebDAV enabled, plus a PUT-based upload test against a chosen WebDAV target using basic auth.",
        "dependencies": ["python3", "shodan", "requests", "SHODAN_API_KEY"],
        "usage": "python3 tomcatscaner.py",
        "notes": "Requires a Shodan API key set in the script before running.",
    },
]

app = FastAPI(title="Security Toolkit Dashboard")


@app.get("/")
def index() -> HTMLResponse:
    return HTMLResponse((STATIC / "index.html").read_text(encoding="utf-8"))


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/tools")
def list_tools() -> JSONResponse:
    enriched = []
    for tool in TOOLS:
        path = ROOT / tool["file"]
        entry = dict(tool)
        entry["exists"] = path.is_file()
        entry["size_bytes"] = path.stat().st_size if path.is_file() else 0
        enriched.append(entry)
    return JSONResponse({"tools": enriched, "total": len(enriched)})
