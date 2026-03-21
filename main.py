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
import parseExpressao
from parseExpressao import AnalisadorLexico, Token, TipoToken

def lerArquivo(nomeArquivo):
    #simulação simples do leitor de arquivos do Aluno 3.
    with open(nomeArquivo, encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]





def gerarAssembly(tokens):
    assembly = []

    for token in tokens:

        if token.tipo in (TipoToken.NUMERO_INTEIRO, TipoToken.NUMERO_REAL):
            assembly.append(f"PUSH {token.valor}")

        elif token.tipo == TipoToken.OPERADOR:
            if token.valor == "+":
                assembly.append("ADD")
            elif token.valor == "-":
                assembly.append("SUB")
            elif token.valor == "*":
                assembly.append("MUL")
            elif token.valor == "/":
                assembly.append("DIV")

        # opcional (depende do trabalho)
        elif token.tipo == TipoToken.KEYWORD and token.valor == "RES":
            assembly.append("OUT")

    assembly.append("OUT")
    return assembly


def executarExpressao(assembly):
    """
    Simula a execução do assembly gerado.
    Usa uma pilha para interpretar as instruções.
    """
    stack = []
    resultado_saida = float('nan')

    for instrucao in assembly:
        partes = instrucao.split()

        if partes[0] == "PUSH":
            stack.append(float(partes[1]))

        elif partes[0] == "ADD":
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)

        elif partes[0] == "SUB":
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)

        elif partes[0] == "MUL":
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)

        elif partes[0] == "DIV":
            b = stack.pop()
            a = stack.pop()
            stack.append(a / b)

        elif partes[0] == "OUT":
            if stack:
                resultado_saida = stack[-1]

    return resultado_saida


def exibirResultados(resultados):
    #exibe os resultados das expressões processadas, formatando para 1 casa decimal.
    print("\nResultados das expressões:\n")

    for i, resultado in enumerate(resultados, start=1):
        try:
            print(f"Linha {i}: {resultado:.1f}")
        except:
            print(f"Linha {i}: {resultado}")


def ProgramTests():
    #testes para validar o programa
    print("\nExecutando testes do programa...\n")

    arquivo = "teste1.txt"
    linhas = lerArquivo(arquivo)

    resultados = []

    for linha in linhas:
        tokens = parseExpressao(linha)
        assembly = gerarAssembly(tokens)
        resultado = executarExpressao(assembly)
        resultados.append(resultado)

    exibirResultados(resultados)


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