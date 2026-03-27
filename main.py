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
from exibirResultados import exibirResultados
from utils import salvar_tokens, salvar_assembly, obter_argumentos_cli, lerArquivo

from executarExpressao import InterpretadorRPN, executarExpressao

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
    
    interpretador = InterpretadorRPN()

    for i, linha in enumerate(linhas, start=1):
        linha_strip = linha.strip()
        
        if not linha_strip or linha_strip.startswith("#"):
            continue

        try:
            analisador.parseExpressao(linha_strip) 

            tokens_da_linha = analisador.matriz_tokens[-1]
            executarExpressao(tokens_da_linha, interpretador)
            
        except Exception as erro:
            print(f"Erro na linha {i}: {erro}")
            sys.exit(1)

    if interpretador.historico:
        for i, resultado in enumerate(interpretador.historico, start=1):
            exibirResultados([resultado], i)

    salvar_tokens(nome_base, analisador.matriz_tokens)

    try:
        gerador = geradorAssembly()
        assembly = gerador.gerarAssembly(analisador.matriz_tokens)
        
        salvar_assembly(nome_base, assembly)

    except Exception as erro:
        print(f"Erro na geração de assembly: {erro}")

if __name__ == "__main__":
    main()