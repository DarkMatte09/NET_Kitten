"""
Modulo Report
-------------
Prende tutti i risultati della scansione e li formatta
in un report leggibile, sia a schermo che su file.
"""

# 'datetime' per aggiungere la data/ora al report
from datetime import datetime


def generate_report(results: dict, output_file: str = None):
    """
    Genera un report dei risultati della scansione.
    
    Parametri:
        results     - dizionario con i risultati (da main.py)
        output_file - percorso file dove salvare il report (opzionale)
    """

    # Separatore visivo
    SEP = "\033[90m" + "─" * 60 + "\033[0m"

    print(f"\n{SEP}")
    print(f"\033[96m  📋 REPORT FINALE\033[0m")
    print(f"\033[90m  Target: {results['target']}")
    print(f"  Data:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    print(SEP)

    # ── Sezione Ping Sweep ──────────────────────────────────
    ping_results = results.get("ping_results", [])
    if ping_results:
        print(f"\n\033[93m  [PING SWEEP] Host attivi trovati: {len(ping_results)}\033[0m")
        for ip in ping_results:
            print(f"\033[92m    ✓ {ip}\033[0m")
    elif "ping_results" in results:
        print(f"\n\033[91m  [PING SWEEP] Nessun host attivo trovato.\033[0m")

    # ── Sezione Port Scan ────────────────────────────────────
    port_results = results.get("port_results", {})
    if port_results:
        total_open = sum(len(ports) for ports in port_results.values())
        print(f"\n\033[93m  [PORT SCAN] Porte aperte totali: {total_open}\033[0m")

        for ip, ports in port_results.items():
            if ports:
                print(f"\n\033[96m  Host: {ip}\033[0m")
                # Intestazione tabella
                print(f"\033[90m  {'PORTA':<10} {'STATO':<10} {'SERVIZIO':<15} {'BANNER'}\033[0m")
                print(f"\033[90m  {'─'*10} {'─'*10} {'─'*15} {'─'*30}\033[0m")
                for p in ports:
                    banner = p['banner'][:30] if p['banner'] else "-"
                    print(f"  \033[92m{p['port']:<10}\033[0m"
                          f"\033[92m{'open':<10}\033[0m"
                          f"\033[96m{p['service']:<15}\033[0m"
                          f"\033[90m{banner}\033[0m")
            else:
                print(f"\n\033[90m  Host {ip}: nessuna porta aperta nel range scansionato.\033[0m")

    # ── Sommario ─────────────────────────────────────────────
    print(f"\n{SEP}")
    print(f"\033[90m  Scansione completata alle {datetime.now().strftime('%H:%M:%S')}\033[0m")
    print(SEP + "\n")

    # ── Salva su file (versione senza colori ANSI) ────────────
    if output_file:
        _save_to_file(results, output_file)


def _save_to_file(results: dict, filepath: str):
    """
    Salva il report in un file di testo (senza codici colore ANSI).
    I codici ANSI come \033[92m rendono il testo colorato a schermo,
    ma in un file di testo diventano caratteri strani.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("  NETSCOUT - REPORT SCANSIONE")
    lines.append("=" * 60)
    lines.append(f"  Target: {results['target']}")
    lines.append(f"  Data:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    ping_results = results.get("ping_results", [])
    if ping_results:
        lines.append(f"\n[PING SWEEP] Host attivi: {len(ping_results)}")
        for ip in ping_results:
            lines.append(f"  + {ip}")

    port_results = results.get("port_results", {})
    if port_results:
        total_open = sum(len(p) for p in port_results.values())
        lines.append(f"\n[PORT SCAN] Porte aperte totali: {total_open}")
        for ip, ports in port_results.items():
            lines.append(f"\n  Host: {ip}")
            if ports:
                lines.append(f"  {'PORTA':<10} {'STATO':<10} {'SERVIZIO':<15} BANNER")
                lines.append(f"  {'-'*10} {'-'*10} {'-'*15} {'-'*30}")
                for p in ports:
                    banner = p['banner'][:30] if p['banner'] else "-"
                    lines.append(f"  {p['port']:<10} {'open':<10} {p['service']:<15} {banner}")
            else:
                lines.append("  Nessuna porta aperta.")

    lines.append("\n" + "=" * 60)

    try:
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        print(f"\033[92m[✓] Report salvato in: {filepath}\033[0m\n")
    except IOError as e:
        print(f"\033[91m[!] Errore nel salvataggio: {e}\033[0m\n")
