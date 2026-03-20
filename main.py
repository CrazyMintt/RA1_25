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


def lerArquivo(nomeArquivo):
    #simulação simples do leitor de arquivos do Aluno 3.
    with open(nomeArquivo, encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]


def parseExpressao(linha):
    #simulação simples do parser do Aluno 1.
    linha = linha.replace("(", "").replace(")", "")
    return linha.split()


def gerarAssembly(tokens):
    #simulação simples do gerador de assembly do Aluno 2.
    assembly = []

    for token in tokens:
        if token.replace('.', '', 1).isdigit():
            assembly.append(f"PUSH {token}")
        elif token == "+":
            assembly.append("ADD")
        elif token == "-":
            assembly.append("SUB")
        elif token == "*":
            assembly.append("MUL")
        elif token == "/":
            assembly.append("DIV")

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
    #flagzinha para controlar a exibição dos resultados
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

    for linha in linhas:
        try:
            tokens = parseExpressao(linha)
            assembly = gerarAssembly(tokens)
            resultado = executarExpressao(assembly)
            resultados.append(resultado)
        except Exception as erro:
            print("Erro ao processar linha:", linha)
            print("Detalhe:", erro)
            resultados.append(float('nan'))

    if mostrar_saida:
        exibirResultados(resultados)


if __name__ == "__main__":
    main()