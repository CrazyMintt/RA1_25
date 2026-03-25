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
        stack: list[float] = []

        for i in range(len(tokens)):
            token = tokens[i]

            # Parênteses são delimitadores de escopo na linguagem, não afeta o RPN logo são ignorados
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
                    # math.trunc para preservar o comportamento correto para floats grandes
                    stack.append(float(math.trunc(a / b)))

                elif token.valor == "%":
                    if b == 0.0:
                        raise Exception(
                            f"Erro na linha {token.linha}: Resto da divisão por zero."
                        )
                    stack.append(float(a - math.trunc(a / b) * b))

                elif token.valor == "^":
                    stack.append(math.pow(a, b))

            # (V MEM) para armazenar e (MEM) para recuperar
            elif token.tipo == TipoToken.MEMORIA:
                eh_atribuicao = self._detectar_atribuicao(tokens, i, stack)

                if eh_atribuicao:
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

                valor_res = self.historico[-n]
                stack.append(valor_res)

        resultado = stack[-1] if stack else 0.0
        return resultado

    def _detectar_atribuicao(self, tokens: list[Token], i_mem: int, stack: list[float]) -> bool:
        # É atribuição se houver valor na pilha e o proximo token relevante for ) ou fim da expressão
        if not stack:
            return False # Pilha vazia, só pode ser leitura

        for j in range(i_mem + 1, len(tokens)):
            tipo = tokens[j].tipo
            if tipo == TipoToken.PARENTESE_DIR:
                return True  # Próximo relevante é ')', atribuição
            if tipo != TipoToken.PARENTESE_ESQ:
                return False # Há outro operando/operador pela frente, leitura

        return True # Fim da expressão com valor na pilha, atribuição


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

    Exmeplo de uso por enquanto: python executarExpressao.py Teste1.txt
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
            analisador.parseExpressao(linha + "\n", numero)
            tokens = analisador.matriz_tokens[-1]
            resultado = executarExpressao(tokens, interpretador)
            resultados.append(resultado)
            # Prints para teste
            print(f"Linha {numero:>2}: {linha:<40} → {resultado}")
        except Exception as e:
            print(f"Linha {numero:>2}: {linha:<40} → ERRO: {e}")
            resultados.append(None)

    return resultados


# ── Testes ───────────────────────────────────────────────────────────────────
# Remover no merge

def _testar():
    # Cada grupo de casos usa instância própria para garantir isolamento total. As variaveis salvas em B ou C não devem ser compartilhadas com A.
    casos = [
        # (descrição, expressão, deve_falhar, grupo)
        ("Soma simples",                "(3.14 2.0 +)",                 False, "A"),
        ("Expressão aninhada",          "((1.5 2.0 *) (3.0 4.0 *) /)",  False, "A"),
        ("Armazenamento em memória",    "(5.0 VAR)",                    False, "A"),
        ("Leitura de memória",          "(VAR)",                        False, "A"),
        ("Leitura de memória não init", "(NOVA)",                       False, "A"),
        ("Potenciação",                 "(2.0 8.0 ^)",                  False, "A"),
        ("Divisão inteira",             "(7.0 2.0 //)",                 False, "A"),
        ("Resto da divisão",            "(7.0 3.0 %)",                  False, "A"),
        # Histórico vazio garante que RES falhe como esperado
        ("RES N=0 inválido",            "(0 RES)",                      True,  "B"),
        ("RES sem histórico",           "(1 RES)",                      True,  "C"),
    ]

    interpretadores = {
        "A": criarInterpretador(),
        "B": criarInterpretador(),
        "C": criarInterpretador(),  # nunca recebe resultado → (1 RES) tem que falhar
    }

    # Um analisador por grupo de testes, assim como um arquivo teria o seu
    analisadores = {
        "A": AnalisadorLexico(),
        "B": AnalisadorLexico(),
        "C": AnalisadorLexico(),
    }

    print("=" * 55)
    print("TESTES executarExpressao")
    print("=" * 55)

    for descricao, expressao, deve_falhar, grupo in casos:
        interp = interpretadores[grupo]
        analisador = analisadores[grupo]
        try:
            analisador.parseExpressao(expressao + "\n", len(analisador.matriz_tokens) + 1)
            tokens = analisador.matriz_tokens[-1]
            resultado = executarExpressao(tokens, interp)
            status = "PASS" if not deve_falhar else "FALHOU (deveria lançar erro)"
            print(f"[{status}] {descricao}: {resultado}")
        except Exception as e:
            status = "PASS (erro esperado)" if deve_falhar else "ERRO INESPERADO"
            print(f"[{status}] {descricao}: {e}")

    print()
    print("Histórico acumulado (grupo A):", interpretadores["A"].historico)
    print()

    # Usa executar() diretamente (sem registrar no histórico) para não "contaminar" o estado entre as verificações de (1 RES) e (2 RES).
    print("--- Teste RES com histórico ---")
    interp_res = criarInterpretador()
    analisador_res = AnalisadorLexico()

    analisador_res.parseExpressao("(3.0 4.0 +)\n", 1)
    executarExpressao(analisador_res.matriz_tokens[-1], interp_res)  # → 7.0

    analisador_res.parseExpressao("(2.0 3.0 *)\n", 2)
    executarExpressao(analisador_res.matriz_tokens[-1], interp_res)  # → 6.0
    # histórico é exatamente [7.0, 6.0]

    analisador_res.parseExpressao("(1 RES)\n", 3)
    r1 = interp_res.executar(analisador_res.matriz_tokens[-1])
    print(f"[{'PASS' if r1 == 6.0 else 'FALHOU'}] (1 RES) esperado 6.0, obtido {r1}")

    analisador_res.parseExpressao("(2 RES)\n", 4)
    r2 = interp_res.executar(analisador_res.matriz_tokens[-1])
    print(f"[{'PASS' if r2 == 7.0 else 'FALHOU'}] (2 RES) esperado 7.0, obtido {r2}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Modo arquivo: python executarExpressao.py teste1.txt [teste2.txt ...]
        for caminho in sys.argv[1:]:
            processarArquivo(caminho)
    else:
        # Modo testes internos
        _testar()