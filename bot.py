import requests
import json
import base64
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permite que seu site admin envie dados para o bot sem bloqueios

# --- CONFIGURAÇÕES DO GITHUB ---
# O ideal é colocar o Token nas 'Environment Variables' do Render com o nome TOKEN
TOKEN = "4750173d50f26347fbeaf97caa056ae5" 
REPO = "victorsilva0965-prog/BFSTORYS"
FILE_PATH = "produtos.json"

def atualizar_github(novo_produto):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. Tenta buscar o arquivo existente
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = response.json()
        sha = content['sha']
        # Decodifica o conteúdo que vem em Base64 do GitHub
        try:
            dados_existentes = json.loads(base64.b64decode(content['content']).decode('utf-8'))
        except:
            dados_existentes = {"status": "online", "estoque": []}

        # Garante que a estrutura 'estoque' existe
        if "estoque" not in dados_existentes:
            dados_existentes["estoque"] = []
            
        # Adiciona o novo produto à lista
        dados_existentes["estoque"].append(novo_produto)
        
        # 2. Codifica novamente para Base64
        json_string = json.dumps(dados_existentes, indent=4, ensure_ascii=False)
        conteudo_codificado = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        
        # 3. Envia a atualização para o GitHub
        payload = {
            "message": f"Bot: Adicionando {novo_produto['nome']} via Painel Admin",
            "content": conteudo_codificado,
            "sha": sha
        }
        
        put_response = requests.put(url, json=payload, headers=headers)
        return put_response.status_code in [200, 201]
    
    return False

@app.route('/')
def home():
    return "Bot BF STORY Online - Pronto para receber cadastros!", 200

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    try:
        dados = request.json
        if not dados:
            return jsonify({"status": "erro", "message": "Dados não recebidos"}), 400
        
        # Monta o objeto exatamente como o seu script.js espera ler
        novo_item = {
            "id": str(dados.get('id', '00')).upper(),
            "nome": dados.get('nome', 'Produto Sem Nome'),
            "preco": dados.get('preco', 'Consultar'),
            "tipo": dados.get('tipo', 'smart'),
            "link": dados.get('link', '#'),
            "specs": dados.get('specs', 'Disponível em nossa loja'),
            "imgs": [dados.get('imagem', 'https://via.placeholder.com/500')]
        }
        
        sucesso = atualizar_github(novo_item)
        
        if sucesso:
            return jsonify({"status": "sucesso", "item": novo_item['nome']}), 200
        else:
            return jsonify({"status": "erro", "message": "Falha ao atualizar GitHub"}), 500
            
    except Exception as e:
        return jsonify({"status": "erro", "message": str(e)}), 500

if __name__ == "__main__":
    # O Render usa a porta 10000 por padrão ou a definida pela variável PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
