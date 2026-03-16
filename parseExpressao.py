from enum import Enum

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
        return self.valor


class AnalisadorLexico:
    linha_atual: int  # Linha do arquivo que está sendo analisada
    coluna_atual: int  # Posição (coluna) da linha que está sendo analisada
    expressao: str  # Conteúdo completo da linha que está sendo analisada
    parenteses: int  # Contador de balanceamento de parenteses

    def __init__(self, expressao: str):
        self.expressao = expressao
        self.linha_atual = 0
        self.coluna_atual = 0
        self.parenteses = 0

    def parseExpressao(self) -> list[Token]:
        """
        Loop principal do programa que faz o parse da expressão.
        """

        tokens: list[Token] = []
        while self.linha_atual < len(self.expressao):
            atual = self.expressao[self.linha_atual]

            if atual in NUMEROS_VALIDOS:
                token = self.estadoNumero()

            elif atual in OPERADORES_VALIDOS:
                token = self.estadoOperador()

            elif atual in PARENTESES:
                token = self.estadoParentese()

            elif atual in COMANDOS_VALIDOS:
                token = self.estadoComando()

            else:
                raise Exception
            tokens.append(token)

        return tokens

    def estadoNumero(self) -> Token:
        lexema: str = ""
        while self.expressao[self.coluna_atual] != SEPARADOR_TOKEN:
            lexema += self.expressao[self.coluna_atual]
            proximo = self.expressao[self.coluna_atual + 1]
            # Lookahead se o próximo valor ainda é um número
            if proximo in NUMEROS_VALIDOS:
                self.coluna_atual += 1
            # Lookahead se é um número decimal
            elif proximo == SEPARADOR_DECIMAL:
                return self.estadoDecimal()
            # Qualquer outra coisa que segue um número é inválido.
            else:
                raise Exception("Token Inválido")
        self.coluna_atual += 1
        return Token(
            tipo=TipoToken.NUMERO_INTEIRO,
            valor=lexema,
            linha=self.linha_atual,
            coluna=self.coluna_atual,
        )

    def estadoDecimal(self) -> Token:
        lexema: str = ""
        # Ainda é o mesmo token até chegar em SEPARADOR_TOKEN
        while self.expressao[self.coluna_atual] != SEPARADOR_TOKEN:
            lexema += self.expressao[self.coluna_atual]
            proximo = self.expressao[self.coluna_atual + 1]
            # Lookahead se o próximo valor ainda é um número
            if proximo in NUMEROS_VALIDOS:
                self.coluna_atual += 1
            # Qualquer outra coisa que segue um número é inválido.
            else:
                raise Exception("Token inválido.")
        # Avança a posição para sair do SEPARADOR_TOKEN
        self.coluna_atual += 1
        return Token(
            tipo=TipoToken.NUMERO_REAL,
            valor=lexema,
            linha=self.linha_atual,
            coluna=self.coluna_atual,
        )

    def estadoOperador(self) -> Token:
        pass

    def estadoParentese(self) -> Token:
        pass

    def estadoComando(self) -> Token:
        pass


analisador = AnalisadorLexico("1 2 +")

analisador.parseExpressao()
