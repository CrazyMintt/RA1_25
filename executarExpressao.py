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
        
        for token in tokens:
            # Ignoramos parênteses na avaliação RPN direta
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
                # Lógica: (V MEM) armazena, (MEM) recupera
                if stack:
                    # Se há valor na pilha, armazena (V MEM)
                    valor = stack.pop()
                    self.memoria[token.valor] = valor
                    # O comando de armazenamento retorna o próprio valor para a pilha?
                    # Se a pilha ficar vazia, retorna o valor armazenado
                    stack.append(valor) 
                else:
                    # Se pilha vazia, recupera (MEM)
                    valor = self.memoria.get(token.valor, 0.0)
                    stack.append(valor)
                
            elif token.tipo == TipoToken.KEYWORD and token.valor == "RES":
                # (N RES) - N deve estar no topo da pilha
                if not stack:
                    raise Exception(f"Erro na linha {token.linha}: Comando RES sem índice.")
                
                n = int(stack.pop())
                if n < 0 or n >= len(self.historico):
                    # Se não houver histórico suficiente, retorna 0.0 ou erro?
                    valor_res = 0.0
                else:
                    # N=0 é o último resultado, N=1 o penúltimo, etc.
                    valor_res = self.historico[-(n + 1)]
                
                stack.append(valor_res)

        resultado = stack[-1] if stack else 0.0
        self.historico.append(resultado)
        return resultado

# Instância global para manter estado entre as linhas do arquivo
_interpretador_global = InterpretadorRPN()

def executarExpressao(tokens: list[Token]):
    return _interpretador_global.executar(tokens)
