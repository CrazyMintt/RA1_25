import sys

from parseExpressao import AnalisadorLexico
from lerArquivo import lerArquivo
from gerarAssembly import geradorAssembly

def main():
    if len(sys.argv) < 2:
        print("Uso correto:")
        print("python main.py arquivo.txt")
        sys.exit(1)

    nomeArquivo = sys.argv[1]

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

    analisador = AnalisadorLexico()

    for i, linha in enumerate(linhas, start=1):
        try:
            analisador.parseExpressao(linha, i)
        except Exception as erro:
            print(f"Erro na linha {i}: {linha}")
            print("Detalhe:", erro)

    for i, tokens in enumerate(analisador.matriz_tokens, start=1):
        try:
            print(f"\n===== LINHA {i} =====")
            print("Tokens:")

            for t in tokens:
                print(t)

            gerador = geradorAssembly()
            assembly = gerador.gerarAssembly(tokens)

            print("\nAssembly gerado:")
            print(assembly)

        except Exception as erro:
            print(f"Erro ao gerar assembly na linha {i}")
            print("Detalhe:", erro)



if __name__ == "__main__":
    main()