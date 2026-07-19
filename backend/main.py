# Importa a classe FastAPI, ponto de partida de toda aplicação com o framework
from fastapi import FastAPI

# Cria a instância da aplicação, que registra as rotas e atende as requisições
app = FastAPI()


# Registra a rota GET /health, usada para verificar se a API está no ar
@app.get("/health")
def read_root():
    # Devolve um dicionário, que o FastAPI converte automaticamente em JSON
    return {"status": "Ok"}
