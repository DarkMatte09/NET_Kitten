"""
Modulo Ping Sweep
-----------------
Invia un ping a ogni host in un range di indirizzi IP
e restituisce la lista di quelli "vivi" (che rispondono).
"""

# 'subprocess' permette di eseguire comandi di sistema da Python
# come se li scrivessi nel terminale
import subprocess

# 'ipaddress' è una libreria Python per gestire indirizzi IP e reti
import ipaddress

# 'concurrent.futures' permette di eseguire più ping contemporaneamente
# (molto più veloce che farli uno alla volta!)
from concurrent.futures import ThreadPoolExecutor, as_completed


def _ping_single(ip: str, timeout: float) -> tuple[str, bool]:
    """
    Esegue un singolo ping verso un IP.
    
    Parametri:
        ip      - l'indirizzo IP da pingare (es: "192.168.1.1")
        timeout - quanti secondi aspettare prima di arrendersi
    
    Ritorna:
        una tupla (ip, True/False) — True se l'host risponde
    """
    try:
        # Costruiamo il comando ping:
        # -c 1 = manda solo 1 pacchetto
        # -W timeout = aspetta al massimo X secondi
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(int(timeout)), ip],
            stdout=subprocess.DEVNULL,   # Nascondi l'output normale
            stderr=subprocess.DEVNULL,   # Nascondi gli errori
            timeout=timeout + 1          # Safety timeout per subprocess
        )
        # returncode == 0 significa che il ping ha avuto successo
        return (ip, result.returncode == 0)
    except subprocess.TimeoutExpired:
        return (ip, False)
    except Exception:
        return (ip, False)


def ping_sweep(target: str, timeout: float = 1.0) -> list[str]:
    """
    Esegue un ping sweep su un range di IP.
    
    Parametri:
        target  - IP singolo o range CIDR (es: "192.168.1.0/24")
        timeout - timeout per ogni ping
    
    Ritorna:
        lista di IP che hanno risposto al ping
    """
    alive_hosts = []

    # Proviamo a interpretare il target come una rete CIDR
    # Se è un IP singolo (es: 192.168.1.1), lo trattiamo come /32
    try:
        # strict=False permette di scrivere 192.168.1.5/24 senza errori
        network = ipaddress.ip_network(target, strict=False)
        hosts = list(network.hosts())  # Tutti gli IP della rete
        if not hosts:
            hosts = [network.network_address]  # IP singolo
    except ValueError:
        print(f"\033[91m[!] Target non valido: {target}\033[0m")
        return []

    total = len(hosts)
    print(f"\033[90m    Scanning {total} hosts con {min(50, total)} thread paralleli...\033[0m")

    # ThreadPoolExecutor esegue più ping in parallelo
    # max_workers = numero massimo di ping contemporanei
    with ThreadPoolExecutor(max_workers=min(50, total)) as executor:
        # Invia tutti i ping contemporaneamente
        futures = {executor.submit(_ping_single, str(ip), timeout): str(ip) for ip in hosts}

        completed = 0
        for future in as_completed(futures):
            ip, is_alive = future.result()
            completed += 1

            # Mostra una barra di avanzamento semplice
            progress = int((completed / total) * 20)
            bar = "█" * progress + "░" * (20 - progress)
            print(f"\r\033[90m    [{bar}] {completed}/{total}\033[0m", end="", flush=True)

            if is_alive:
                alive_hosts.append(ip)
                print(f"\n\033[92m    [+] Host attivo: {ip}\033[0m")

    print()  # Vai a capo dopo la barra
    return sorted(alive_hosts)  # Ritorna ordinati
