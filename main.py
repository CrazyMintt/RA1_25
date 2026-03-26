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
from gerarAssembly import geradorAssembly
from utils import salvar_tokens, salvar_assembly, obter_argumentos_cli, lerArquivo

def main():
    caminho_arquivo, nome_base = obter_argumentos_cli()

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

    except Exception as erro:
        print(f"Erro na geração de assembly: {erro}")

if __name__ == "__main__":
    main()