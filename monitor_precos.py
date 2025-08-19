# =================================================================
# VERSÃO 2.1 - Robô de Monitoramento Multi-Produtos
# Pronto para rodar em servidores como o PythonAnywhere ou GitHub Actions
# =================================================================

# Passo 1: Importar todas as ferramentas necessárias
import requests
from bs4 import BeautifulSoup
import re
import time
import os # ESSENCIAL: Para ler as "variáveis de ambiente" de forma segura

# =================================================================
# Passo 2: Carregar suas informações secretas do ambiente
# No GitHub Actions, isso será configurado nos "Secrets" do repositório.
# =================================================================
TELEGRAM_TOKEN = os.environ.get('MEU_TOKEN_TELEGRAM')
TELEGRAM_CHAT_ID = os.environ.get('MEU_CHAT_ID_TELEGRAM')


# =================================================================
# Passo 3: Sua lista de produtos para monitorar
# =================================================================
lista_produtos = [
    {
        "nome": "Fone de ouvido JBL Tune 510BT",
        "url": "https://www.amazon.com.br/Fone-ouvido-Bluetooth-Tune-510BT/dp/B08WM3LMJF/",
        "preco_alvo": 300.00 # Aumentei o preço para forçar o alerta nos testes
    },
    {
        "nome": "Echo Dot 5ª geração",
        "url": "https://www.amazon.com.br/Echo-Dot-5ª-geração-Cor-Preta/dp/B09B8VGCR8/",
        "preco_alvo": 400.00 # Aumentei o preço para forçar o alerta nos testes
    },
]


# =================================================================
# Passo 4: Função que envia a mensagem para o Telegram
# =================================================================
def enviar_alerta_telegram(mensagem):
    """Envia uma mensagem formatada para o chat especificado no Telegram."""
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url_telegram, data=payload)
        print("Alerta enviado para o Telegram com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar alerta para o Telegram: {e}")


# =================================================================
# Passo 5: A função principal que verifica os preços
# =================================================================
def verificar_produtos():
    """Passa por cada produto na lista e verifica o preço."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    
    for produto in lista_produtos:
        print(f"--- Verificando: {produto['nome']} ---")
        
        try:
            pagina = requests.get(produto['url'], headers=headers)
            sopa = BeautifulSoup(pagina.content, "html.parser")
            elemento_preco = sopa.find("span", class_="a-offscreen")

            if elemento_preco:
                preco_texto = elemento_preco.get_text()
                preco_limpo = preco_texto.replace("R$", "").strip().replace(".", "").replace(",", ".")
                preco_atual_float = float(preco_limpo)
                
                print(f"Preço encontrado: R$ {preco_atual_float:.2f}")

                if preco_atual_float < produto['preco_alvo']:
                    print("O preço está ABAIXO do alvo! Enviando alerta...")
                    mensagem_alerta = (
                        f"🚨 <b>ALERTA DE PREÇO!</b> 🚨\n\n"
                        f"<b>Produto:</b> {produto['nome']}\n"
                        f"<b>Preço Atual:</b> R$ {preco_atual_float:.2f}\n"
                        f"<b>Preço Alvo:</b> R$ {produto['preco_alvo']:.2f}\n\n"
                        f"<b>Link:</b>\n{produto['url']}"
                    )
                    enviar_alerta_telegram(mensagem_alerta)
                else:
                    print("Preço acima do alvo. Nenhuma ação.")
            else:
                print("Elemento do preço não encontrado para este produto.")
        
        except Exception as e:
            print(f"Ocorreu um erro ao verificar o produto {produto['nome']}: {e}")

        print("Pausa de 3 segundos...\n")
        time.sleep(3)


# =================================================================
# Passo 6: Iniciar a verificação
# =================================================================
if __name__ == "__main__":
    if TELEGRAM_TOKEN is None or TELEGRAM_CHAT_ID is None:
        print("ERRO CRÍTICO: As variáveis de ambiente (Secrets) MEU_TOKEN_TELEGRAM e MEU_CHAT_ID_TELEGRAM não foram configuradas.")
    else:
        print("Iniciando verificação de produtos...")
        verificar_produtos()
        print("--- Fim da verificação de todos os produtos ---")
