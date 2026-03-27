import sys
import os

def salvar_tokens(nome_base, matriz_tokens):
    nome_saida = f"{nome_base}_tokens.txt"
    try:
        with open(nome_saida, 'w', encoding='utf-8') as f:
            for i, linha_tokens in enumerate(matriz_tokens, start=1):
                f.write(f"Linha {i}: ")
                # Converte cada objeto Token em string para salvar
                tokens_str = [f"[{t.tipo.name}: {t.valor}]" for t in linha_tokens]
                f.write(" ".join(tokens_str) + "\n")
        print(f"Tokens salvos com sucesso em: {nome_saida}")
    except Exception as e:
        print(f"Erro ao salvar tokens: {e}")


def salvar_assembly(nome_base, codigo_assembly):
    nome_saida = f"{nome_base}.s"
    try:
        with open(nome_saida, 'w', encoding='utf-8') as f:
            f.write(codigo_assembly)
        print(f"Código Assembly salvo com sucesso em: {nome_saida}")
    except Exception as e:
        print(f"Erro ao salvar assembly: {e}")


def obter_argumentos_cli():
    if len(sys.argv) < 2:
        print("Uso: python main.py arquivo.txt")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    
    if not caminho_arquivo.lower().endswith(".txt"):
        print("Erro: o arquivo deve ser .txt")
        sys.exit(1)
    nome_base = os.path.splitext(os.path.basename(caminho_arquivo))[0]
    
    return caminho_arquivo, nome_base

def ler_arquivo(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as file:
        linhas = file.read().splitlines()
    return linhas