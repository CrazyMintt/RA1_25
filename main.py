"""
Aluno 4 - Interface do Usuário, exibirResultados e testes

Responsabilidades:
- Implementar exibirResultados
- Implementar main
- Chamar funções dos outros módulos:
    lerArquivo
    parseExpressao
    gerarAssembly
    executarExpressao
"""

import sys

import executarExpressao
import lerArquivo
import gerarAssembly
import exibirResultados
from parseExpressao import AnalisadorLexico, Token, TipoToken



def main():

    if len(sys.argv) < 2:
        print("Uso correto:")
        print("python main.py arquivo.txt [--no-output]")
        sys.exit(1)

    nomeArquivo = sys.argv[1]

    mostrar_saida = True
    if "--no-output" in sys.argv:
        mostrar_saida = False

    if not nomeArquivo.lower().endswith(".txt"):
        print("Erro: o arquivo de entrada deve ser do tipo .txt")
        sys.exit(1)

    try:
        linhas = lerArquivo(nomeArquivo)
        if not linhas:
            print("O arquivo está vazio.")
            sys.exit(1)
    except Exception as erro:
        print("Erro ao ler arquivo:", erro)
        sys.exit(1)

    resultados = []

    for i, linha in enumerate(linhas, start=1):
        try:
            analisador = AnalisadorLexico(linha)
            tokens = analisador.parseExpressao()

            assembly = gerarAssembly(tokens)
            resultado = executarExpressao(assembly)

            resultados.append(resultado)

        except Exception as erro:
            print(f"Erro na linha {i}: {linha}")
            print("Detalhe:", erro)
            resultados.append(float('nan'))

    if mostrar_saida:
        exibirResultados(resultados)


if __name__ == "__main__":
    main()