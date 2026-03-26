'''
Equipe:
Bruno Betiatto Alves @Brunobetiatto
Bruno Himovski Opuszka Machado Dutra @CrazyMintt 
Leonardo Saito @Leosaito632 
Vitor Nicoletti @vitorNicoletti

GRUPO: RA1-25   
'''

import sys
from parseExpressao import AnalisadorLexico
from lerArquivo import lerArquivo
from gerarAssembly import geradorAssembly

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py arquivo.txt")
        sys.exit(1)

    nomeArquivo = sys.argv[1]
    
    if not nomeArquivo.lower().endswith(".txt"):
        print("Erro: o arquivo deve ser .txt")
        sys.exit(1)
    try:
        linhas = lerArquivo(nomeArquivo)
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
    try:
        gerador = geradorAssembly()
        assembly, pilha = gerador.gerarAssembly(analisador.matriz_tokens)
        print(assembly)
    except Exception as erro:
        print(f"Erro na geração de assembly: {erro}")

if __name__ == "__main__":
    main()