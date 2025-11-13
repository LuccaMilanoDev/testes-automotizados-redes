import csv
import time
import requests
from ping3 import ping
from urllib.parse import urlparse  # <--- IMPORTANTE

# Lista de hosts e endpoints (pode ser IP ou domínio)
hosts = [
    "8.8.8.8",
    "1.1.1.1",
    "https://www.google.com",
    "https://www.github.com",
    "https://example.com",
    "192.168.1.1",       # IP local (provavelmente vai falhar o ping se não for seu roteador)
    "https://naoexiste.dominio" # Teste de falha
]

resultados = []

print("🌐 Iniciando teste de conectividade e serviço web...\n")

for host_original in hosts:
    inicio_total = time.time()

    # --- Preparação do Alvo ---
    # Precisamos do hostname limpo para o ping
    # e da URL completa para o HTTP
    
    # Por padrão, o alvo do ping é o host original (caso seja um IP)
    host_para_ping = host_original
    
    # Se for uma URL, extrai o hostname (ex: 'www.google.com')
    if host_original.startswith("http"):
        try:
            parsed_url = urlparse(host_original)
            host_para_ping = parsed_url.hostname 
        except Exception:
            # Se a URL for mal formatada, pula para o próximo
            print(f"🔹 {host_original}\n   URL mal formatada. Pulando...\n")
            continue
    
    if host_para_ping is None:
        print(f"🔹 {host_original}\n   Não foi possível extrair hostname. Pulando...\n")
        continue

    # --- Teste de Ping (ICMP) ---
    ping_status = False
    try:
        # Usar o host_para_ping (ex: 'www.google.com' ou '8.8.8.8')
        resposta_ping = ping(host_para_ping, timeout=2)
        if resposta_ping is not None:
            ping_status = True
    except Exception as e:
        # Captura erros de DNS (ex: 'naoexiste.dominio') ou permissão
        ping_status = False

    # --- Teste de HTTP/HTTPS ---
    http_status = None
    http_code = None
    
    # Só executa o teste HTTP se o host original for uma URL
    if host_original.startswith("http"):
        try:
            resposta = requests.get(host_original, timeout=3)
            http_code = resposta.status_code
            # Consideramos sucesso qualquer código 2xx (ex: 200 OK)
            http_status = (http_code >= 200 and http_code < 300)
        except requests.exceptions.RequestException:
            # Captura falhas de conexão, timeout, erro de DNS, etc.
            http_status = False
    
    fim_total = time.time()
    duracao = round(fim_total - inicio_total, 2)

    resultados.append({
        "host": host_original,
        "ping_ok": ping_status,
        "http_ok": http_status,
        "http_code": http_code,
        "tempo_execucao": duracao
    })

    # --- Exibição no console (Lógica de print melhorada) ---
    ping_str = '✅' if ping_status else '❌'
    
    if http_status is True:
        http_str = f"✅ (HTTP {http_code})"
    elif http_status is False:
        # Se http_status for False, significa que tentou e falhou
        http_str = f"❌ (HTTP {http_code})" if http_code else "❌ (Falha na Conexão)"
    else:
        # Se http_status for None, significa que não era http (era só IP)
        http_str = "N/A"

    print(f"🔹 {host_original} (Alvo do Ping: {host_para_ping})")
    print(f"   Ping: {ping_str} | HTTP: {http_str} | Tempo: {duracao}s\n")

# --- Salvar resultados em CSV ---
try:
    with open("resultados.csv", "w", newline="", encoding="utf-8") as f:
        campos = ["host", "ping_ok", "http_ok", "http_code", "tempo_execucao"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)
    print("📄 Teste finalizado! Resultados salvos em resultados.csv")
except IOError:
    print("❌ Erro: Não foi possível salvar o arquivo 'resultados.csv'. Verifique as permissões.")