import requests
import json
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÕES DO GITHUB ---
TOKEN = "4750173d50f26347fbeaf97caa056ae5"
REPO = "victorsilva0965-prog/BFSTORYS"
FILE_PATH = "produtos.json"

# --- FUNÇÃO PARA ENVIAR AO GITHUB ---
def atualizar_github(novo_produto):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. Pega o arquivo atual
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        sha = content['sha']
        # Decodifica o JSON antigo
        dados_antigos = json.loads(base64.b64decode(content['content']).decode('utf-8'))
        
        # Garante que a estrutura está correta (estoque)
        if isinstance(dados_antigos, dict) and "estoque" in dados_antigos:
            dados_antigos["estoque"].append(novo_produto)
        else:
            dados_antigos = {"status": "online", "estoque": [novo_produto]}
            
        # 2. Envia a versão atualizada
        novo_conteudo = base64.b64encode(json.dumps(dados_antigos, indent=4).encode('utf-8')).decode('utf-8')
        payload = {"message": f"Adicionando {novo_produto['nome']}", "content": novo_conteudo, "sha": sha}
        requests.put(url, json=payload, headers=headers)
        return True
    return False

# --- ROTA QUE O SEU PAINEL VAI CHAMAR ---
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.json
    
    # Aqui o bot monta o produto com o que recebeu do seu site
    novo_item = {
        "id": dados.get('id', '00').upper(),
        "nome": dados.get('nome'),
        "preco": dados.get('preco'),
        "tipo": dados.get('tipo', 'smart'),
        "link": dados.get('link', '#'),
        "specs": dados.get('specs', 'Produto de alta qualidade'),
        "imgs": [dados.get('imagem', 'https://via.placeholder.com/500')]
    }
    
    sucesso = atualizar_github(novo_item)
    
    if sucesso:
        return jsonify({"status": "sucesso", "item": novo_item['nome']}), 200
    else:
        return jsonify({"status": "erro"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
      
