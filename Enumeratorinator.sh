#!/bin/bash

# Open a new terminal and elevate to root
gnome-terminal -- bash -c "echo 'kali' | sudo -S su"

# Ask user for the target IP or hostname
read -p 'Enter Target IP or Hostname: ' TARGET_IP
read -p 'Enter Target Domain (e.g., example.com): ' TARGET_DOMAIN

echo "=================================================="
echo "[+] Target IP: $TARGET_IP"
echo "[+] Target Domain: $TARGET_DOMAIN"
echo "=================================================="

# Initial Nmap Scan (Find Open Ports)
echo "[+] Running initial Nmap scan to detect open ports..."
OPEN_PORTS=$(nmap -Pn -sS -p- "$TARGET_IP" --min-rate=3000 --max-retries 1 --open | tee nmap_initial_scan.txt | awk -F '/' '/open/ {print $1}' | tr '\n' ',' | sed 's/,$//')

# Display Open Ports
echo "--------------------------------------------------"
if [ -z "$OPEN_PORTS" ]; then
    echo "[!] No open ports found!"
    exit 1
else
    echo "[+] Open Ports Found: $OPEN_PORTS"
fi
echo "--------------------------------------------------"

# Run detailed Nmap scan on open ports
echo "[+] Running detailed Nmap scan on open ports..."
nmap -Pn -sS -p"$OPEN_PORTS" -A "$TARGET_IP" | tee nmap_detailed_scan.txt

# Run Gobuster for directory enumeration (include non-accessible directories like 403)
echo "[+] Running Gobuster for directory enumeration..."
gobuster dir -u http://"$TARGET_DOMAIN" -w /usr/share/wordlists/dirb/big.txt -t 100 -k -b 301,404 -a "Mozilla/12.3" -r | tee gobuster_dir_scan.txt

# Extract directories with 200 OK or 403 Forbidden for recursion and further analysis
echo "[+] Checking for discovered directories..."
DISCOVERED_DIRS=$(grep -E "200 \(OK\)|403 \(Forbidden\)" gobuster_dir_scan.txt | awk '{print $2, $3, $4}')

# Display discovered directories
echo "--------------------------------------------------"
if [ -z "$DISCOVERED_DIRS" ]; then
    echo "[!] No accessible or restricted directories found!"
else
    echo "[+] Discovered Directories:"
    echo "$DISCOVERED_DIRS"
fi
echo "--------------------------------------------------"

# Run recursive scans on directories that returned 200 OK
RECURSIVE_DIRS=$(grep "200 (OK)" gobuster_dir_scan.txt | awk '{print $2}')
if [ -n "$RECURSIVE_DIRS" ]; then
    echo "[+] Recursively scanning directories that returned 200 OK..."
    for DIR in $RECURSIVE_DIRS; do
        echo "[🔄] Scanning: $DIR"
        gobuster dir -u http://"$TARGET_DOMAIN$DIR" -w /usr/share/wordlists/dirb/big.txt -t 100 -k -b 301,404 -a "Mozilla/12.3" -r | tee "gobuster_recursive_$DIR.txt"
    done
else
    echo "[!] No directories found for recursion."
fi

# Check for directory listing (index of files)
echo "[+] Checking for directory listing vulnerabilities..."
for DIR in $RECURSIVE_DIRS; do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://"$TARGET_DOMAIN$DIR")
    if [[ "$RESPONSE" == "200" ]]; then
        PAGE_CONTENT=$(curl -s http://"$TARGET_DOMAIN$DIR")
        if echo "$PAGE_CONTENT" | grep -q "Index of"; then
            echo "[⚠] Directory Listing Enabled: $TARGET_DOMAIN$DIR"
            echo "[⚠] Possible sensitive files can be accessed!"
        fi
    fi
done

# Run Gobuster for DNS enumeration and store results
echo "[+] Running Gobuster for DNS subdomain enumeration..."
DNS_RESULTS=$(gobuster dns -d "$TARGET_DOMAIN" -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-20000.txt -t 100 | tee gobuster_dns_scan.txt | grep "Found:" | awk '{print $2}')

echo "--------------------------------------------------"
if [ -z "$DNS_RESULTS" ]; then
    echo "[!] No subdomains found."
else
    echo "[+] Subdomains Found:"
    echo "$DNS_RESULTS"
fi
echo "--------------------------------------------------"

# Add found subdomains to /etc/hosts
if [ -n "$DNS_RESULTS" ]; then
    echo "[+] Adding found subdomains to /etc/hosts..."
    for SUBDOMAIN in $DNS_RESULTS; do
        # Check if the subdomain already exists in /etc/hosts
        if ! grep -q "$SUBDOMAIN" /etc/hosts; then
            echo "[✔] Adding: $TARGET_IP $SUBDOMAIN"
            echo "$TARGET_IP $SUBDOMAIN" | sudo tee -a /etc/hosts > /dev/null
        else
            echo "[!] $SUBDOMAIN already exists in /etc/hosts. Skipping..."
        fi
    done
    echo "[+] Subdomains successfully added to /etc/hosts!"
fi

echo "=================================================="
echo "[✔] Scan Completed! All results are saved in:"
echo "  - nmap_initial_scan.txt"
echo "  - nmap_detailed_scan.txt"
echo "  - gobuster_dir_scan.txt"
echo "  - gobuster_recursive_*.txt"
echo "  - gobuster_dns_scan.txt"
echo "=================================================="
