"""
Modulo Port Scanner
-------------------
Tenta di connettersi alle porte di un host per capire
quali sono aperte e quale servizio ci gira sopra.
"""

# 'socket' è la libreria Python per le connessioni di rete
# Permette di aprire connessioni TCP/UDP agli host
import socket

# 'concurrent.futures' per scansionare più porte in parallelo
from concurrent.futures import ThreadPoolExecutor, as_completed

# 'ipaddress' per gestire range di IP
import ipaddress


# Dizionario delle porte più comuni e i loro servizi
# Questo ci permette di dire "la porta 80 è HTTP" invece di solo "80/open"
COMMON_SERVICES = {
    21:   "FTP",
    22:   "SSH",
    23:   "Telnet",
    25:   "SMTP",
    53:   "DNS",
    80:   "HTTP",
    110:  "POP3",
    143:  "IMAP",
    443:  "HTTPS",
    445:  "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    27017: "MongoDB",
}


def _parse_port_range(ports_str: str) -> list[int]:
    """
    Converte una stringa di porte in una lista di interi.
    
    Esempi:
        "80"        → [80]
        "1-1024"    → [1, 2, 3, ..., 1024]
        "80,443,22" → [80, 443, 22]
    """
    ports = []
    for part in ports_str.split(","):
        part = part.strip()
        if "-" in part:
            # Range: "1-1024"
            start, end = part.split("-")
            ports.extend(range(int(start), int(end) + 1))
        else:
            # Porta singola: "80"
            ports.append(int(part))
    return ports


def _grab_banner(sock: socket.socket) -> str:
    """
    Tenta di leggere un "banner" dal servizio.
    Alcuni servizi (FTP, SSH, SMTP) inviano automaticamente
    un messaggio di benvenuto che rivela la versione del software.
    
    Es: "SSH-2.0-OpenSSH_8.4p1"
    """
    try:
        sock.settimeout(2)
        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        # Prendi solo la prima riga e troncala a 60 caratteri
        return banner.split("\n")[0][:60]
    except Exception:
        return ""


def _scan_port(ip: str, port: int, timeout: float) -> dict | None:
    """
    Tenta una connessione TCP alla porta specificata.
    
    Parametri:
        ip      - indirizzo IP target
        port    - numero di porta da testare
        timeout - timeout della connessione
    
    Ritorna:
        dict con info sulla porta se aperta, None se chiusa/filtrata
    """
    try:
        # Crea un socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        # connect_ex ritorna 0 se la connessione ha successo
        # (a differenza di connect() che lancia un'eccezione)
        result = sock.connect_ex((ip, port))

        if result == 0:
            # Porta aperta! Proviamo a leggere il banner
            banner = _grab_banner(sock)
            sock.close()

            # Cerca il nome del servizio nel nostro dizionario
            service = COMMON_SERVICES.get(port, "unknown")

            return {
                "port":    port,
                "state":   "open",
                "service": service,
                "banner":  banner,
            }
        sock.close()
        return None

    except Exception:
        return None


def port_scan(target: str, ports_str: str = "1-1024", timeout: float = 1.0) -> dict:
    """
    Scansiona le porte di uno o più host.
    
    Parametri:
        target    - IP singolo o range CIDR
        ports_str - stringa di porte (es: "1-1024" o "80,443,22")
        timeout   - timeout per ogni connessione
    
    Ritorna:
        dict { "192.168.1.1": [{"port": 80, "state": "open", ...}, ...], ... }
    """
    ports = _parse_port_range(ports_str)

    # Ricava la lista di IP target
    try:
        network = ipaddress.ip_network(target, strict=False)
        hosts = [str(ip) for ip in network.hosts()]
        if not hosts:
            hosts = [str(network.network_address)]
    except ValueError:
        hosts = [target]

    all_results = {}

    for ip in hosts:
        print(f"\033[90m    Scansione di {len(ports)} porte su {ip}...\033[0m")
        open_ports = []

        # Scansiona fino a 100 porte contemporaneamente
        with ThreadPoolExecutor(max_workers=min(100, len(ports))) as executor:
            futures = {executor.submit(_scan_port, ip, port, timeout): port for port in ports}

            completed = 0
            for future in as_completed(futures):
                completed += 1
                result = future.result()

                # Aggiorna barra progresso
                progress = int((completed / len(ports)) * 20)
                bar = "█" * progress + "░" * (20 - progress)
                print(f"\r\033[90m    [{bar}] {completed}/{len(ports)}\033[0m", end="", flush=True)

                if result:
                    open_ports.append(result)
                    banner_str = f" → \"{result['banner']}\"" if result['banner'] else ""
                    print(f"\n\033[92m    [+] {ip}:{result['port']}/tcp  {result['service']}{banner_str}\033[0m")

        print()  # Vai a capo
        # Ordina le porte aperte per numero di porta
        all_results[ip] = sorted(open_ports, key=lambda x: x["port"])

    return all_results
