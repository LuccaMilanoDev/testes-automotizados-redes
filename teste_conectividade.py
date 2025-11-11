import csv
from datetime import datetime
from ping3 import ping

# Caminho dos arquivos
ARQUIVO_HOSTS = "hosts.txt"
ARQUIVO_RESULTADOS = "resultados.csv"

def carregar_hosts(caminho_arquivo):
    """Lê os hosts do arquivo e retorna uma lista"""
    try:
        with open(caminho_arquivo, "r") as f:
            hosts = [linha.strip() for linha in f.readlines() if linha.strip()]
        return hosts
    except FileNotFoundError:
        print(f"❌ Arquivo {caminho_arquivo} não encontrado.")
        return []

def testar_conectividade(host):
    """Executa o ping e retorna o resultado"""
    try:
        resposta = ping(host, timeout=2)
        if resposta is not None:
            return (True, round(resposta * 1000, 2))  # tempo em ms
        else:
            return (False, None)
    except Exception as e:
        print(f"⚠️ Erro ao pingar {host}: {e}")
        return (False, None)

def salvar_resultados(resultados):
    """Salva os resultados em CSV"""
    with open(ARQUIVO_RESULTADOS, "w", newline="") as csvfile:
        escritor = csv.writer(csvfile)
        escritor.writerow(["Host", "Status", "Tempo de resposta (ms)", "Data/Hora"])
        for host, status, tempo in resultados:
            escritor.writerow([
                host,
                "Ativo" if status else "Inativo",
                tempo if tempo is not None else "-",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

def main():
    print("🔍 Iniciando teste de conectividade...\n")
    hosts = carregar_hosts(ARQUIVO_HOSTS)
    if not hosts:
        return

    resultados = []
    for host in hosts:
        status, tempo = testar_conectividade(host)
        if status:
            print(f"✅ {host} está ativo — {tempo} ms")
        else:
            print(f"❌ {host} está inativo ou inacessível")
        resultados.append((host, status, tempo))

    salvar_resultados(resultados)
    print("\n📄 Teste finalizado! Resultados salvos em resultados.csv")

if __name__ == "__main__":
    main()
