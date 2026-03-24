from parseExpressao import Token, TipoToken
import math

class InterpretadorRPN:
    def __init__(self):
        # Dicionário para gerenciar múltiplas variáveis na memória (MEM)
        self.memoria = {}
        # Histórico de resultados para suportar (N RES)
        self.historico = []

    def executar(self, tokens: list[Token]):
        stack = []
        
        for i in range(len(tokens)):
            token = tokens[i]
            
            if token.tipo in [TipoToken.PARENTESE_ESQ, TipoToken.PARENTESE_DIR]:
                continue

            if token.tipo in [TipoToken.NUMERO_INTEIRO, TipoToken.NUMERO_REAL]:
                stack.append(float(token.valor))
            
            elif token.tipo == TipoToken.OPERADOR:
                if len(stack) < 2:
                    raise Exception(f"Erro na linha {token.linha}: Operador '{token.valor}' sem operandos suficientes.")
                
                b = stack.pop()
                a = stack.pop()
                
                if token.valor == "+":
                    stack.append(a + b)
                elif token.valor == "-":
                    stack.append(a - b)
                elif token.valor == "*":
                    stack.append(a * b)
                elif token.valor == "/":
                    if b == 0: raise Exception("Divisão por zero.")
                    stack.append(a / b)
                elif token.valor == "//":
                    if b == 0: raise Exception("Divisão inteira por zero.")
                    stack.append(float(int(a) // int(b)))
                elif token.valor == "%":
                    if b == 0: raise Exception("Resto por zero.")
                    stack.append(float(int(a) % int(b)))
                elif token.valor == "^":
                    stack.append(math.pow(a, b))
            
            elif token.tipo == TipoToken.MEMORIA:
                # Lógica de Atribuição vs Busca
                proximo_is_fim = False
                if i + 1 < len(tokens):
                    if tokens[i+1].tipo == TipoToken.PARENTESE_DIR:
                        proximo_is_fim = True
                else:
                    proximo_is_fim = True

                if proximo_is_fim and stack:
                    valor = stack.pop()
                    self.memoria[token.valor] = valor
                    stack.append(valor) 
                else:
                    valor = self.memoria.get(token.valor, 0.0)
                    stack.append(valor)
                
            elif token.tipo == TipoToken.KEYWORD and token.valor == "RES":
                if not stack:
                    raise Exception(f"Erro na linha {token.linha}: Comando RES sem índice.")
                
                n = int(stack.pop())
                if n < 0 or n >= len(self.historico):
                    valor_res = 0.0
                else:
                    # N=0 é a última linha, N=1 a penúltima...
                    valor_res = self.historico[-(n + 1)]
                
                stack.append(valor_res)

        resultado = stack[-1] if stack else 0.0
        return resultado

    def prepararExpressaoParaAssembly(self, tokens: list[Token]):
        """
        Método solicitado para lidar com parênteses aninhados.
        Retorna uma lista de tokens em RPN pura, facilitando a geração de Assembly
        pelo Aluno 3, removendo a necessidade de tratar parênteses lá.
        """
        rpn_pura = []
        for t in tokens:
            if t.tipo not in [TipoToken.PARENTESE_ESQ, TipoToken.PARENTESE_DIR]:
                rpn_pura.append(t)
        return rpn_pura

# Instância global
_interpretador_global = InterpretadorRPN()

def executarExpressao(tokens: list[Token]):
    res = _interpretador_global.executar(tokens)
    _interpretador_global.historico.append(res)
    return res

def lidarComParentesesAninhados(tokens: list[Token]):
    return _interpretador_global.prepararExpressaoParaAssembly(tokens)
