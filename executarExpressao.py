from parseExpressao import Token, TipoToken
import math

class InterpretadorRPN:
    def __init__(self):
        # Gerenciamento de múltiplas variáveis na memória
        self.memoria = {}
        # Histórico de resultados para suportar (N RES)
        self.historico = []

    def executar(self, tokens: list[Token]):
        stack = []
        
        # Filtrar parênteses para a execução RPN (estruturais)
        # Na RPN pura parênteses são ignorados, mas aqui eles vão delimitar o escopo.
        
        for token in tokens:
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
                # Se houver algo na pilha, pode ser uma atribuição (V MEM)
                # Se não, é uma recuperação (MEM)
                pass
                
            elif token.tipo == TipoToken.KEYWORD and token.valor == "RES":
                # (N RES) - N deve estar no topo da pilha
                pass

        if not stack:
            return 0.0
        
        resultado = stack[-1]
        self.historico.append(resultado)
        return resultado

# Instância global para manter estado entre linhas (escopo do arquivo)
_interpretador_global = InterpretadorRPN()

def executarExpressao(tokens: list[Token]):
    return _interpretador_global.executar(tokens)
