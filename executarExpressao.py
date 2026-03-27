'''
Equipe:
Bruno Betiatto Alves @Brunobetiatto
Bruno Himovski Opuszka Machado Dutra @CrazyMintt 
Leonardo Saito @Leosaito632 
Vitor Nicoletti @vitorNicoletti

GRUPO: RA1-25   
'''

from parseExpressao import Token, TipoToken, AnalisadorLexico
import math

class InterpretadorRPN:
    def __init__(self):
        # Dicionário para as variaveis de memoria
        self.memoria: dict[str, float] = {}
        # historico[0] = resultado da linha 1, historico[1] = resultado da linha 2, etc.
        self.historico: list[float] = []

    def resetar(self):
        self.memoria = {}
        self.historico = []

    def executar(self, tokens: list[Token]) -> float:
        # Ponto de entrada: resolve os parênteses de dentro para fora
        tokens_resolvidos = self._resolver_parenteses(tokens)
        return self._avaliar_plano(tokens_resolvidos)

    def _resolver_parenteses(self, tokens: list[Token]) -> list[Token]:
        tokens = list(tokens)
        while True:
            # Procura o primeiro ')' e seu '(' correspondente
            i_dir = None
            for idx, t in enumerate(tokens):
                if t.tipo == TipoToken.PARENTESE_DIR:
                    i_dir = idx
                    break

            if i_dir is None:
                break  # Sem mais parênteses

            # Encontra o '(' que abre este grupo
            i_esq = None
            for idx in range(i_dir - 1, -1, -1):
                if tokens[idx].tipo == TipoToken.PARENTESE_ESQ:
                    i_esq = idx
                    break

            if i_esq is None:
                raise Exception("Parêntese de fechamento sem abertura correspondente.")

            # Avalia o conteúdo entre os parênteses (já sem parênteses internos)
            tokens_internos = tokens[i_esq + 1 : i_dir]
            valor = self._avaliar_plano(tokens_internos)

            token_resultado = Token(
                tipo=TipoToken.NUMERO_REAL,
                valor=str(valor),
                linha=tokens[i_esq].linha,
                coluna=tokens[i_esq].coluna,
            )
            tokens[i_esq : i_dir + 1] = [token_resultado]

        return tokens

    def _avaliar_plano(self, tokens: list[Token]) -> float:
        """
        tenta pop da pilha; se houver valor → atribuição;
        se pilha vazia → leitura.
        """
        stack: list[float] = []

        for token in tokens:
            if token.tipo in [TipoToken.PARENTESE_ESQ, TipoToken.PARENTESE_DIR]:
                continue

            if token.tipo in [TipoToken.NUMERO_INTEIRO, TipoToken.NUMERO_REAL]:
                stack.append(float(token.valor))

            elif token.tipo == TipoToken.OPERADOR:
                if len(stack) < 2:
                    raise Exception(
                        f"Erro na linha {token.linha}: "
                        f"Operador '{token.valor}' sem operandos suficientes."
                    )

                b = stack.pop()
                a = stack.pop()

                if token.valor == "+":
                    stack.append(a + b)

                elif token.valor == "-":
                    stack.append(a - b)

                elif token.valor == "*":
                    stack.append(a * b)

                elif token.valor == "/":
                    if b == 0.0:
                        raise Exception(
                            f"Erro na linha {token.linha}: Divisão por zero."
                        )
                    stack.append(a / b)

                elif token.valor == "//":
                    if b == 0.0:
                        raise Exception(
                            f"Erro na linha {token.linha}: Divisão inteira por zero."
                        )
                    stack.append(float(math.trunc(a / b)))

                elif token.valor == "%":
                    if b == 0.0:
                        raise Exception(
                            f"Erro na linha {token.linha}: Resto da divisão por zero."
                        )
                    stack.append(a % b)

                elif token.valor == "^":
                    stack.append(math.pow(a, b))

            elif token.tipo == TipoToken.MEMORIA:
                # pop = atribuição; 
                # pilha vazia = leitura.
                
                if stack:
                    valor = stack.pop()
                    self.memoria[token.valor] = valor
                    stack.append(valor)
                else:
                    valor = self.memoria.get(token.valor, 0.0)
                    stack.append(valor)

            elif token.tipo == TipoToken.KEYWORD and token.valor == "RES":
                if not stack:
                    raise Exception(
                        f"Erro na linha {token.linha}: Comando RES sem índice na pilha."
                    )

                n = int(stack.pop())

                if n <= 0:
                    raise Exception(
                        f"Erro na linha {token.linha}: "
                        f"RES exige N >= 1 (N=0 causaria recursividade infinita). "
                        f"Use (1 RES) para o resultado da linha anterior."
                    )

                if n > len(self.historico):
                    raise Exception(
                        f"Erro na linha {token.linha}: "
                        f"RES {n} inválido — só existem {len(self.historico)} linha(s) anteriores."
                    )

                stack.append(self.historico[-n])

        return stack[-1] if stack else 0.0


# A função executarExpressao recebe o interpretador como parâmetro para garantir escopo independente por arquivo
def criarInterpretador() -> InterpretadorRPN:
    return InterpretadorRPN()

def executarExpressao(tokens: list[Token], interpretador: InterpretadorRPN) -> float:
    """
    Executa uma expressão RPN representada por tokens, registra o resultado
    no histórico do interpretador fornecido e o retorna.
    """
    res = interpretador.executar(tokens)
    interpretador.historico.append(res)
    return res


def processarArquivo(caminho: str) -> list[float]:
    """
    Lê um arquivo de expressões RPN (uma por linha), executa cada linha
    e retorna a lista de resultados.

    Exemplo de uso: python executarExpressao.py Teste1.txt
    """
    interpretador = criarInterpretador()
    resultados: list[float] = []

    with open(caminho, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()

    analisador = AnalisadorLexico()

    print(f"\nProcessando: {caminho}")
    print("=" * 55)

    for numero, linha in enumerate(linhas, start=1):
        linha = linha.strip()
        if not linha or linha.startswith("#"): # ignora linhas vazias e comentários
            continue
        try:
            analisador.parseExpressao(linha)
            tokens = analisador.matriz_tokens[-1]
            resultado = executarExpressao(tokens, interpretador)
            resultados.append(resultado)
            # Prints para teste
            print(f"Linha {numero:>2}: {linha:<40} → {resultado}")
        except Exception as e:
            print(f"Linha {numero:>2}: {linha:<40} → ERRO: {e}")
            resultados.append(None)

    return resultados

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Modo arquivo: python executarExpressao.py teste1.txt [teste2.txt ...]
        for caminho in sys.argv[1:]:
            processarArquivo(caminho)