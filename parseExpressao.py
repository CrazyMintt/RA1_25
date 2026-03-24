from enum import Enum

SEPARADOR_TOKEN = " "
SEPARADOR_DECIMAL = "."
NUMEROS_VALIDOS = [str(i) for i in range(0, 10)]
OPERADORES_VALIDOS = ["+", "-", "*", "/", "%", "^"]
RES_KEYWORD = "RES"
PARENTESES_DIR = "("
PARENTESE_ESQ = ")"


class ErroLexico(Exception):
    """Classe base para erros do analisador léxico."""

    def __init__(self, mensagem: str, linha: int, coluna: int):
        super().__init__(f"Erro na linha {linha}, coluna {coluna}: {mensagem}")
        self.linha = linha
        self.coluna = coluna


class ErroTokenInvalido(ErroLexico):
    def __init__(self, char: str, linha: int, coluna: int):
        super().__init__(f"Caractere ou token inválido '{char}'.", linha, coluna)


class TipoToken(Enum):
    NUMERO_INTEIRO = 1
    NUMERO_REAL = 2
    OPERADOR = 3
    MEMORIA = 4
    KEYWORD = 5
    PARENTESE_ESQ = 6
    PARENTESE_DIR = 7


class Token:

    def __init__(
        self,
        tipo: TipoToken | None = None,
        valor: str = "",
        linha: int = 0,
        coluna: int = 0,
    ):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __str__(self):
        return f"Tipo: {self.tipo}, Valor: {self.valor}, Linha: {self.linha}, Coluna: {self.coluna}"


class AnalisadorLexico:
    linha_atual: int  # Linha do arquivo que está sendo analisada
    coluna_atual: int  # Posição (coluna) da linha que está sendo analisada
    expressao: str  # Conteúdo completo da linha que está sendo analisada
    # Matriz para armazenar todos os tokens de todas as expressoes (linhas)
    matriz_tokens: list[list[Token]]

    def __init__(self):
        self.linha_atual = 0
        self.coluna_atual = 0
        self.matriz_tokens = []

    def is_fim_token(self) -> bool:
        # O fim de um token é o espaço " " ou um parêntese esquerdo ")"
        return self.peek_atual() == SEPARADOR_TOKEN or self.peek_atual == ")"

    def avancar(self):
        """Avanca um char e atualiza as posições"""
        if self.coluna_atual < len(self.expressao):
            self.coluna_atual += 1

    def peek_atual(self) -> str:
        """Olha se o caractere atual é o final sem atualizar posição"""
        if self.coluna_atual < len(self.expressao):
            return self.expressao[self.coluna_atual]
        else:
            return ""  # String vazia se for o fim

    def parseExpressao(self, expressao: str, numero_linha: int):
        """Função chamada para cada linha (expressão) que será analisada"""

        # Prepara o estado para a nova linha
        self.expressao = expressao
        self.linha_atual = numero_linha
        self.coluna_atual = 0

        self.estadoInicial()

    def estadoInicial(self):
        atual = self.peek_atual()
        token = Token(coluna=self.coluna_atual)

        if atual in NUMEROS_VALIDOS:
            self.estadoNumero(token=token)

        elif atual in OPERADORES_VALIDOS:
            self.estadoOperador(token)

        elif atual in PARENTESES:
            self.estadoParentese(self.coluna_atual)

        # Keyword RES
        elif atual == "R":
            self.estadoComandoRes(self.coluna_atual)

        # Identificadores de Memória são compostos de letras maíusculas
        elif atual.isalpha() and atual.isupper():
            self.estadoComandoMemoria(col_inicio=self.coluna_atual, lexema=None)
        else:
            self.estadoErro(token)

    def estadoNumero(self, token: Token):
        # Define o tipo do Token como NUMERO_INTEIRO
        token.tipo = TipoToken.NUMERO_INTEIRO
        # Adiciona o valor atual ao valor do Token
        token.valor += self.peek_atual()

        self.avancar()

        if self.peek_atual() in NUMEROS_VALIDOS:
            self.estadoNumero(token)
        elif self.peek_atual() == SEPARADOR_DECIMAL:
            self.estadoDecimal(token)
        elif self.is_fim_token():
            self.estadoFimToken(token)

    def estadoDecimal(self, token: Token):
        """Estado para números com casas decimais.
        A parte inteira do número ja deve estar no Token"""

        # Muda o tipo do Token para NUMERO_REAL
        token.tipo = TipoToken.NUMERO_REAL
        # Adiciona o valor da posição atual ao valor do token
        token.valor += self.peek_atual()

        self.avancar()

        if self.peek_atual() in NUMEROS_VALIDOS:
            self.estadoDecimal(token)
        elif self.is_fim_token():
            self.estadoFimToken(token)
        else:
            self.estadoErro(token)

    def estadoOperador(self, token: Token):
        token.tipo = TipoToken.OPERADOR
        token.valor = self.peek_atual()
        self.avancar()

        if self.peek_atual() == "/":
            self.estadoDivisaoInteiro(token)
        elif self.is_fim_token():
            self.estadoFimToken(token)
        else:
            self.estadoErro(token)

    def estadoDivisaoInteiro(self, token: Token):
        token.tipo = TipoToken.OPERADOR
        token.valor += self.peek_atual()
        self.avancar()

        if self.is_fim_token():
            self.estadoFimToken(token)
        else:
            self.estadoErro(token)

    def estadoParenteseDir(self, token: Token):
        self.tipo = TipoToken.PARENTESE_DIR
        self.valor = self.peek_atual()
        self.avancar()

        if self.peek_atual() == SEPARADOR_TOKEN:
            self.estadoFimToken(token)
        else:
            self.estadoErro(token)

    def estadoParenteseEsq(self, token: Token):
        self.tipo = TipoToken.PARENTESE_ESQ
        self.valor = self.peek_atual()
        self.avancar()

        if self.peek_atual() == SEPARADOR_TOKEN:
            self.estadoFimToken(token)
        else:
            self.estadoErro(token)

    def estadoComandoR(self, token: Token):
        self.tipo = TipoToken.KEYWORD
        self.valor = self.peek_atual()

        if self.peek_atual() == "E":
            self.estadoComandoE(token)

    def estadoComandoE(self, token: Token):
        self.tipo = TipoToken.KEYWORD
        self.valor = self.peek_atual()

        if self.peek_atual() == "S":
            self.estadoComandoE(token)

    def estadoComandoS(self, token: Token):
        self.tipo = TipoToken.KEYWORD
        self.valor = self.peek_atual()

        if self.is_fim_token():
            self.estadoFimToken(token)

    def estadoComandoMemoria(self, col_inicio: int, lexema: str | None) -> Token:
        # Se lexema não foi inicializado ainda, inicializa com o atual
        if not lexema:
            lexema = self.peek_atual()
            self.avancar()

        while self.peek_atual().isalpha():
            if not self.peek_atual().isupper():
                raise ErroTokenInvalido(
                    "Caractere minúsculo encontrado no Identificador de Memória",
                    self.linha_atual,
                    self.coluna_atual,
                )
            lexema += self.peek_atual()
            self.avancar()

        return Token(
            tipo=TipoToken.MEMORIA,
            valor=lexema,
            linha=self.linha_atual,
            coluna=col_inicio,
        )

    def estadoFimToken(self, token: Token):
        self.matriz_tokens.append([token])

    def estadoErro(self, token: Token):
        raise ErroTokenInvalido("", token.linha, token.coluna)


if __name__ == "__main__":
    analisador = AnalisadorLexico()

    analisador.parseExpressao("1.0 3 - 5 9 * (1.5 X) RES 1.1 () RESRES", 1)
    analisador.parseExpressao("1.0 3 - 5 9 * (1.5 X) RES 1.1 () RESRES", 2)
    for i in analisador.matriz_tokens:
        for j in i:
            print(j)
