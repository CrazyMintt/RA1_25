
import sys
from parseExpressao import AnalisadorLexico
from lerArquivo import lerArquivo



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

    for i, linha in enumerate(linhas, start=1):
        try:
            analisador = AnalisadorLexico(linha)
            tokens = analisador.parseExpressao()

            for token in tokens:
                print(token)

        except Exception as erro:
            print(f"Erro na linha {i}: {linha}")
            print("Detalhe:", erro)

if __name__ == "__main__":
    main()