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
    COMANDO = 5
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
                token = self.estadoNumero()

            elif atual in OPERADORES_VALIDOS:
                token = self.estadoOperador()

            elif atual in PARENTESES:
                token = self.estadoParentese()

            # Comandos são compostos de letras maíusculas
            elif atual.isalpha() and atual.isupper():
                token = self.estadoComando()

            else:
                raise Exception(f"Token inválido: {atual}")

            tokens.append(token)

        # Verifica se os parenteses estão balanceados
        if self.parenteses != 0:
            raise Exception("Parênteses desbalanceados.")
        return tokens

    def estadoNumero(self) -> Token:
        # No token deve ficar a posicao do inicio do token
        coluna_inicio = self.coluna_atual

        # Inicializa o lexema com o char que entrou nesse estado
        lexema: str = self.expressao[self.pos]
        self.avancar()

        # Por padrão o tipo é INTEIRO
        tipo: TipoToken = TipoToken.NUMERO_INTEIRO

        # Loop para identificar o token inteiro
        while (
            self.peek_atual() in NUMEROS_VALIDOS
            or self.peek_atual() == SEPARADOR_DECIMAL
        ):

            atual = self.peek_atual()

            # Validação de decimal
            if atual == SEPARADOR_DECIMAL:
                # caso já tenha um separador decimal é inválido
                if SEPARADOR_DECIMAL in lexema:
                    raise Exception("Token Inválido: dois pontos decimais")
                tipo = TipoToken.NUMERO_REAL  # Muda o tipo do token

            # Atualiza o lexema e avança
            lexema += atual
            self.avancar()

        # Retorna ao chegar no fim da expressão
        # ou encontrar um char que não é relacionado à número
        return Token(
            tipo=tipo,
            valor=lexema,
            linha=self.linha_atual,
            coluna=coluna_inicio,
        )

    def estadoOperador(self) -> Token:
        coluna_inicio = self.coluna_atual
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
            coluna=coluna_inicio,
        )

    def estadoParentese(self) -> Token:
        # Incializa lexema com char que entrou nesse estado
        coluna_inicio = self.coluna_atual
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
            coluna=coluna_inicio,
        )

    def estadoComando(self) -> Token:
        coluna_inicio = self.coluna_atual
        comando = self.peek_atual()
        self.avancar()

        while self.peek_atual().isalpha():
            if not self.peek_atual().isupper():
                raise Exception("Caractere minúsculo encontrado em comando")
            comando += self.peek_atual()
            self.avancar()

        if comando == RES_KEYWORD:
            tipo = TipoToken.COMANDO
        else:
            tipo = TipoToken.MEMORIA

        return Token(
            tipo=tipo,
            valor=comando,
            linha=self.linha_atual,
            coluna=coluna_inicio,
        )


analisador = AnalisadorLexico("1 3 - 5 9 * (1.5 X) RES 1.1 ()")


for t in analisador.parseExpressao():
    print(t)

print("-----------")
print("TODO:")
print("Lidar com multiplas linhas (múltiplas expressões)")
print("Exceptions mais específicas")
