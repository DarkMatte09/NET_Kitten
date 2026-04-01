#!/usr/bin/env python3
"""
NETSCOUT - Network Reconnaissance Tool
Autore: [Il tuo nome qui]
Licenza: MIT
"""

# 'argparse' è una libreria Python che gestisce i parametri da terminale
# Es: python netscout.py --target 192.168.1.1 --scan ports
import argparse
import sys
from modules.ping import ping_sweep
from modules.scanner import port_scan
from modules.report import generate_report

# Questo è il "banner" che appare quando avvii il tool
BANNER = """
\033[91m
 ███╗   ██╗███████╗████████╗███████╗ ██████╗ ██████╗ ██╗   ██╗████████╗
 ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔═══██╗██║   ██║╚══██╔══╝
 ██╔██╗ ██║█████╗     ██║   ███████╗██║     ██║   ██║██║   ██║   ██║   
 ██║╚██╗██║██╔══╝     ██║   ╚════██║██║     ██║   ██║██║   ██║   ██║   
 ██║ ╚████║███████╗   ██║   ███████║╚██████╗╚██████╔╝╚██████╔╝   ██║   
 ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   
\033[0m
\033[90m  Network Reconnaissance Tool | For authorized use only\033[0m
\033[90m  ─────────────────────────────────────────────────────\033[0m
"""

def main():
    # Stampa il banner all'avvio
    print(BANNER)

    # Configura i parametri accettati dal tool
    # argparse legge quello che scrivi dopo "python netscout.py ..."
    parser = argparse.ArgumentParser(
        description="NETSCOUT - Network Reconnaissance Tool",
        epilog="Esempio: python netscout.py --target 192.168.1.0/24 --scan all"
    )

    # --target: l'IP o la rete su cui operare (obbligatorio)
    parser.add_argument(
        "--target",
        required=True,
        help="IP singolo (192.168.1.1) o range CIDR (192.168.1.0/24)"
    )

    # --scan: cosa fare (ping, ports, o tutto)
    parser.add_argument(
        "--scan",
        choices=["ping", "ports", "all"],
        default="all",
        help="Tipo di scansione: ping | ports | all (default: all)"
    )

    # --ports: quali porte controllare (opzionale)
    parser.add_argument(
        "--ports",
        default="1-1024",
        help="Range di porte da scansionare (default: 1-1024)"
    )

    # --output: salva il report su file
    parser.add_argument(
        "--output",
        help="Salva il report in un file .txt (es: --output report.txt)"
    )

    # --timeout: quanto aspettare per ogni connessione (in secondi)
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Timeout per ogni probe in secondi (default: 1.0)"
    )

    # Leggi i parametri inseriti dall'utente
    args = parser.parse_args()

    # Dizionario che raccoglierà tutti i risultati
    results = {
        "target": args.target,
        "ping_results": [],
        "port_results": {},
    }

    # Esegui ping sweep se richiesto
    if args.scan in ["ping", "all"]:
        print(f"\033[93m[*] Avvio Ping Sweep su {args.target}...\033[0m")
        results["ping_results"] = ping_sweep(args.target, args.timeout)

    # Esegui port scan se richiesto
    if args.scan in ["ports", "all"]:
        print(f"\033[93m[*] Avvio Port Scan su {args.target} (porte {args.ports})...\033[0m")
        results["port_results"] = port_scan(args.target, args.ports, args.timeout)

    # Genera il report finale
    generate_report(results, args.output)


# Questo blocco dice: "esegui main() solo se questo file è lanciato direttamente"
# (non se viene importato da un altro script)
if __name__ == "__main__":
    main()
