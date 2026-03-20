from enum import Enum

QUEBRA_LINHA = "\n"
SEPARADOR_TOKEN = " "
SEPARADOR_DECIMAL = "."
NUMEROS_VALIDOS = [str(i) for i in range(0, 10)]
OPERADORES_VALIDOS = ["+", "-", "*", "/", "%", "^"]
RES_KEYWORD = "RES"
PARENTESES = ["(", ")"]


class TipoToken(Enum):
    NUMERO_INTEIRO = 1
    NUMERO_REAL = 2
    OPERADOR = 3
    MEMORIA = 4
    KEYWORD = 5
    PARENTESE_ESQ = 6
    PARENTESE_DIR = 7


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

    def avancar(self):
        """Avanca um char e atualiza as posições"""
        if self.pos < len(self.expressao):
            atual = self.expressao[self.pos]

            # Se for outra linha, reseta coluna e incrementa linha
            if atual == QUEBRA_LINHA:
                self.coluna_atual = 0
                self.linha_atual += 1
            else:
                self.coluna_atual += 1
            self.pos += 1

    def peek_atual(self) -> str:
        """Olha se o caractere atual é o final sem atualizar posição"""
        if self.pos < len(self.expressao):
            return self.expressao[self.pos]
        else:
            return ""  # String vazia se for o fim

    def parseExpressao(self) -> list[Token]:
        """
        Loop principal do programa que faz o parse da expressão.
        """

        tokens: list[Token] = []
        while self.peek_atual():
            atual = self.expressao[self.pos]

            # Ignora espaços em branco e quebra de linha
            # Fazer tratamento de quebra de linha depois
            if atual in [SEPARADOR_TOKEN, QUEBRA_LINHA]:
                self.avancar()
                continue

            if atual in NUMEROS_VALIDOS:
                token = self.estadoNumero(self.coluna_atual)

            elif atual in OPERADORES_VALIDOS:
                token = self.estadoOperador(self.coluna_atual)

            elif atual in PARENTESES:
                token = self.estadoParentese(self.coluna_atual)

            # Keyword RES
            elif atual == "R":
                token = self.estadoComandoRes(self.coluna_atual)

            # Identificadores de Memória são compostos de letras maíusculas
            elif atual.isalpha() and atual.isupper():
                token = self.estadoComandoMemoria(
                    col_inicio=self.coluna_atual, lexema=None
                )

            else:
                raise Exception("Token inválido")

            tokens.append(token)

        # Verifica se os parenteses estão balanceados
        if self.parenteses != 0:
            raise Exception("Parênteses desbalanceados.")
        return tokens

    def estadoNumero(self, col_inicio: int) -> Token:
        # Inicializa o lexema com o char que entrou nesse estado
        lexema: str = self.peek_atual()
        self.avancar()

        # Loop para identificar o token inteiro
        while self.peek_atual() in NUMEROS_VALIDOS:
            # Atualiza o lexema e avança
            lexema += self.peek_atual()
            self.avancar()

        if self.peek_atual() == SEPARADOR_DECIMAL:
            return self.estadoDecimal(lexema, col_inicio)

        # Retorna ao chegar no fim da expressão
        # ou encontrar um char que não é relacionado à número
        return Token(
            tipo=TipoToken.NUMERO_INTEIRO,
            valor=lexema,
            linha=self.linha_atual,
            coluna=col_inicio,
        )

    def estadoDecimal(self, parte_inteira: str, col_inicio: int) -> Token:
        """Estado para números com casas decimais.
        A parte inteira do número (antes do '.') deve ser
        passada como parâmetro, assim a coluna incial do número."""

        # Inicializa o lexema com a parte inteira + a posição atual (deve ser SEPARADOR_DECIMAL)
        lexema: str = parte_inteira + self.peek_atual()
        self.avancar()

        # Loop para identificar o token inteiro
        while self.peek_atual() in NUMEROS_VALIDOS:

            atual = self.peek_atual()

            # Atualiza o lexema e avança
            lexema += atual
            self.avancar()

        # Adiciona um 0 se o ultimo char do lexema for .
        # if lexema[-1] == SEPARADOR_DECIMAL:
        #    lexema += "0"

        if self.peek_atual() == SEPARADOR_DECIMAL:
            raise Exception(
                "Token inválido: dois separadores de número decimal (.) encontrados."
            )

        # Retorna ao chegar no fim da expressão
        # ou encontrar um char que não é relacionado à número
        return Token(
            tipo=TipoToken.NUMERO_REAL,
            valor=lexema,
            linha=self.linha_atual,
            coluna=col_inicio,
        )

    def estadoOperador(self, col_inicio: int) -> Token:
        # Incializa lexema com char que entrou nesse estado
        lexema: str = self.expressao[self.pos]
        self.avancar()

        # O único operador composto por 2 chars é //
        if self.peek_atual() == "/":
            lexema += self.expressao[self.pos]
            self.avancar()

        return Token(
            tipo=TipoToken.OPERADOR,
            valor=lexema,
            linha=self.linha_atual,
            coluna=col_inicio,
        )

    def estadoParentese(self, col_inicio: int) -> Token:
        # Incializa lexema com char que entrou nesse estado
        lexema: str = self.expressao[self.pos]
        self.avancar()

        if lexema == "(":
            tipo = TipoToken.PARENTESE_ESQ
            self.parenteses += 1
        elif lexema == ")":
            tipo = TipoToken.PARENTESE_DIR
            self.parenteses -= 1
        else:
            # Nunca deveria chegar aqui
            raise Exception("Entrada no Estado de Parentese com token inválido")

        return Token(
            tipo=tipo,
            valor=lexema,
            linha=self.linha_atual,
            coluna=col_inicio,
        )

    def estadoComandoRes(self, col_inicio: int) -> Token:
        lexema = self.peek_atual()
        self.avancar()

        # R -> E
        if self.peek_atual() == "E":
            lexema += self.peek_atual()
            self.avancar()
            # R -> E -> S
            if self.peek_atual() == "S":
                lexema += self.peek_atual()
                self.avancar()
                # R -> E -> S -> FIM
                if not self.peek_atual().isalpha():
                    return Token(
                        tipo=TipoToken.KEYWORD,
                        valor=lexema,
                        linha=self.linha_atual,
                        coluna=col_inicio,
                    )

        # R -> FIM = Identificador de Memória
        # R -> ... -> LETRA_MAIUSCULA = Identificador de Memória
        if not self.peek_atual() or (
            self.peek_atual().isalpha() and self.peek_atual().isupper()
        ):
            return self.estadoComandoMemoria(col_inicio, lexema)

        return Token(
            tipo=TipoToken.KEYWORD,
            valor=lexema,
            linha=self.linha_atual,
            coluna=col_inicio,
        )

    def estadoComandoMemoria(self, col_inicio: int, lexema: str | None) -> Token:
        # Se lexema não foi inicializado ainda, inicializa com o atual
        if not lexema:
            lexema = self.peek_atual()
            self.avancar()

        while self.peek_atual().isalpha():
            if not self.peek_atual().isupper():
                raise Exception(
                    "Caractere minúsculo encontrado no Identificador de Memória"
                )
            lexema += self.peek_atual()
            self.avancar()

        return Token(
            tipo=TipoToken.MEMORIA,
            valor=lexema,
            linha=self.linha_atual,
            coluna=col_inicio,
        )


analisador = AnalisadorLexico("1. 3 - 5 9 * (1.5 X) RES 1.1 () RESRES")


for t in analisador.parseExpressao():
    print(t)

print("-----------")
print("TODO:")
print("Lidar com multiplas linhas (múltiplas expressões)")
print("Exceptions mais específicas")
