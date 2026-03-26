'''
Equipe:
Bruno Betiatto Alves @Brunobetiatto
Bruno Himovski Opuszka Machado Dutra @CrazyMintt 
Leonardo Saito @Leosaito632 
Vitor Nicoletti @vitorNicoletti

GRUPO: RA1-25   
'''

import sys
import os
from parseExpressao import AnalisadorLexico
from lerArquivo import lerArquivo
from gerarAssembly import geradorAssembly

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

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py arquivo.txt")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    # Extrai o nome do arquivo sem a extensão para usar como prefixo
    nome_base = os.path.splitext(os.path.basename(caminho_arquivo))[0]
    
    if not caminho_arquivo.lower().endswith(".txt"):
        print("Erro: o arquivo deve ser .txt")
        sys.exit(1)

    try:
        linhas = lerArquivo(caminho_arquivo)
        if not linhas:
            print("Arquivo vazio.")
            sys.exit(1)
    except Exception as erro:
        print(f"Erro na leitura: {erro}")
        sys.exit(1)

    analisador = AnalisadorLexico()
    for i, linha in enumerate(linhas, start=1):
        try:
            analisador.parseExpressao(linha) 
        except Exception as erro:
            print(f"Erro léxico na linha {i}: {erro}")

    salvar_tokens(nome_base, analisador.matriz_tokens)
    try:
        gerador = geradorAssembly()
        assembly, pilha = gerador.gerarAssembly(analisador.matriz_tokens)
        
        salvar_assembly(nome_base, assembly)
        
        print("\n--- Preview do Assembly Gerado ---")
        print(assembly)
        
    except Exception as erro:
        print(f"Erro na geração de assembly: {erro}")

if __name__ == "__main__":
    main()