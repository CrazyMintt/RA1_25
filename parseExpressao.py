from enum import Enum

QUEBRA_LINHA = "\n"
SEPARADOR_TOKEN = " "
SEPARADOR_DECIMAL = "."
NUMEROS_VALIDOS = [str(i) for i in range(0, 10)]
OPERADORES_VALIDOS = ["+", "-", "*", "/", "%", "^"]
COMANDOS_VALIDOS = ["MEM", "RES"]
PARENTESES = ["(", ")"]


class TipoToken(Enum):
    NUMERO_INTEIRO = 1
    NUMERO_REAL = 2
    OPERADOR = 3
    COMANDO = 4
    PARENTESE_ESQ = 5
    PARENTESE_DIR = 6


class Token:
    tipo: TipoToken
    valor: str
    linha: int
    coluna: int

    def __init__(self, tipo: TipoToken, valor: str, linha: int, coluna: int):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __str__(self):
        return f"Tipo: {self.tipo}, Valor: {self.valor}"


class AnalisadorLexico:
    pos: int  # Posição geral da string que está sendo analisada
    linha_atual: int  # Linha do arquivo que está sendo analisada
    coluna_atual: int  # Posição (coluna) da linha que está sendo analisada
    expressao: str  # Conteúdo completo da linha que está sendo analisada
    parenteses: int  # Contador de balanceamento de parenteses

    def __init__(self, expressao: str):
        self.pos = 0
        self.expressao = expressao
        self.linha_atual = 0
        self.coluna_atual = 0
        self.parenteses = 0

    def parseExpressao(self) -> list[Token]:
        """
        Loop principal do programa que faz o parse da expressão.
        """

        tokens: list[Token] = []
        while self.pos < len(self.expressao):
            atual = self.expressao[self.pos]

            # Ignora espaços em branco
            if atual == SEPARADOR_TOKEN:
                self.pos += 1
                self.coluna_atual += 1
                continue

            # Condição para próxima linha (próxima expressão)
            elif atual == QUEBRA_LINHA:
                self.linha_atual += 1
                self.coluna_atual = 0
                self.pos += 1
                continue

            if atual in NUMEROS_VALIDOS:
                token = self.estadoNumero()

            elif atual in OPERADORES_VALIDOS:
                token = self.estadoOperador()

            elif atual in PARENTESES:
                token = self.estadoParentese()
            #
            #            elif atual in COMANDOS_VALIDOS:
            #                token = self.estadoComando()
            #

            else:
                print(atual)
                raise Exception

            tokens.append(token)

        # Verifica se os parenteses estão balanceados
        if self.parenteses != 0:
            raise Exception("Parênteses desbalanceados.")
        return tokens

    def estadoNumero(self) -> Token:
        # Inicializa o lexema com o char que entrou nesse estado
        lexema: str = self.expressao[self.pos]
        self.pos += 1
        self.coluna_atual += 1

        # Por padrão o tipo é INTEIRO
        tipo: TipoToken = TipoToken.NUMERO_INTEIRO

        # Loop para identificar o token inteiro
        while self.pos < len(self.expressao):
            atual = self.expressao[self.pos]

            # É um número válido
            if atual in NUMEROS_VALIDOS:
                lexema += atual

            # É um número decimal
            elif atual == SEPARADOR_DECIMAL:
                # caso já tenha um separador decimal é inválido
                if SEPARADOR_DECIMAL in lexema:
                    raise Exception("Token Inválido: dois pontos decimais")

                lexema += atual
                tipo = TipoToken.NUMERO_REAL  # Muda o tipo do token

            # Qualquer outra coisa significa que o token acabou
            else:
                break
            self.coluna_atual += 1
            self.pos += 1
        return Token(
            tipo=tipo,
            valor=lexema,
            linha=self.linha_atual,
            coluna=self.coluna_atual,
        )

    def estadoOperador(self) -> Token:
        lexema: str = self.expressao[self.pos]
        self.pos += 1
        self.coluna_atual += 1

        # O único operador composto por 2 chars é //
        if self.pos < len(self.expressao) and self.expressao[self.pos] == "/":
            lexema += self.expressao[self.pos]
            self.coluna_atual += 1
            self.pos += 1

        return Token(
            tipo=TipoToken.OPERADOR,
            valor=lexema,
            linha=self.linha_atual,
            coluna=self.coluna_atual,
        )

    def estadoParentese(self) -> Token:
        lexema: str = self.expressao[self.pos]
        self.pos += 1
        self.coluna_atual += 1

        if lexema == "(":
            tipo = TipoToken.PARENTESE_ESQ
            self.parenteses += 1
        else:
            tipo = TipoToken.PARENTESE_DIR
            self.parenteses -= 1

        return Token(
            tipo=tipo,
            valor=lexema,
            linha=self.linha_atual,
            coluna=self.coluna_atual,
        )


#
#    def estadoComando(self) -> Token:
#        pass
#

analisador = AnalisadorLexico(
    "1.31+21.1 + - + - //+ 1 () 12312 131 1.1 3. () () () (()) (((())))"
)


for t in analisador.parseExpressao():
    print(t)

print("-----------")
print("TODO:")
print("Função estadoComando")
print("Função para ver se está no fim da expressão pra não ficar repitindo a condição")
print("Função para avançar posição (self.pos e self.col)")
print("Lidar com multiplas linhas (múltiplas expressões)")
print("Exceptions mais específicas")
