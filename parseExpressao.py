# Grupo: RA1 25
# Bruno Betiatto Alves - Brunobetiatto
# Bruno Himovski Opuszka Machado Dutra - CrazyMintt
# Leonardo Saito - Leosaito632
# Vitor Nicoletti - vitorNicoletti
from enum import Enum

SEPARADOR_EXPRESSAO = "\n"
SEPARADOR_TOKEN = " "
SEPARADOR_DECIMAL = "."
NUMEROS_VALIDOS = [str(i) for i in range(0, 10)]
OPERADORES_VALIDOS = ["+", "-", "*", "/", "%", "^"]
RES_KEYWORD = "RES"
PARENTESE_ESQ = "("
PARENTESE_DIR = ")"


class ErroLexico(Exception):
    """Classe base para erros do analisador léxico."""

    def __init__(self, mensagem: str, linha: int, coluna: int):
        super().__init__(f"Erro na linha {linha}, coluna {coluna}: {mensagem}")
        self.linha = linha
        self.coluna = coluna


class ErroTokenInvalido(ErroLexico):
    def __init__(self, char: str, linha: int, coluna: int):
        super().__init__(f"Caractere ou token inválido '{char}'.", linha, coluna)


class ErroExpressaoInvalida(Exception):
    def __init__(self, mensagem: str):
        super().__init__(f"Erro ao criar Tokens da Expressão: {mensagem}")


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
    tokens_linha_atual: list[Token] = []  # Tokens da expressao atual
    # Matriz para armazenar todos os tokens de todas as expressoes (linhas)
    matriz_tokens: list[list[Token]]

    def __init__(self):
        self.linha_atual = 0
        self.coluna_atual = 0
        self.expressao = ""
        self.tokens_linha_atual = []
        self.matriz_tokens = []

    def is_fim_token(self) -> bool:
        """O fim de um token é o espaço ' ' ou um parêntese direito ')'"""
        return self.get_atual() == SEPARADOR_TOKEN or self.get_atual() == PARENTESE_DIR

    def avancar(self):
        """Avanca um char e atualiza a posição"""
        self.coluna_atual += 1

    def get_atual(self) -> str:
        """Retorna o Caractere atual"""
        if self.coluna_atual < len(self.expressao):
            return self.expressao[self.coluna_atual]
        else:
            raise ErroExpressaoInvalida(
                "Caractere sinalizando fim da expressão não encontrado. (\\n)"
            )

    def parseExpressao(self, expressao: str, numero_linha: int):
        """
        Função chamada para cada linha (expressão) que será analisada.
        A `expressão` deve ser uma string de caracteres válidos,
        com quebra de linha `\\n` no final para delimitar o fim da expressão
        """

        # Prepara o estado para a nova linha
        self.expressao = expressao
        self.linha_atual = numero_linha
        self.coluna_atual = 0
        self.tokens_linha_atual = []

        self.estadoInicial()

    def estadoInicial(self, token: Token | None = None):
        # Se receber um token, adiciona à lista de tokens
        if token:
            self.tokens_linha_atual.append(token)

        atual = self.get_atual()
        token = Token(linha=self.linha_atual, coluna=self.coluna_atual)

        # Chegou no fim da expressao
        if not atual:
            # Adiciona a linha lida à matriz
            self.matriz_tokens.append(self.tokens_linha_atual)

        # Ignora espacos vazios (volta pro estado inicial)
        elif atual == SEPARADOR_TOKEN:
            self.avancar()
            self.estadoInicial()

        elif atual in NUMEROS_VALIDOS:
            self.estadoNumero(token=token)

        elif atual in OPERADORES_VALIDOS:
            self.estadoOperador(token)

        elif atual == PARENTESE_DIR:
            self.estadoParenteseDir(token)

        elif atual == PARENTESE_ESQ:
            self.estadoParenteseEsq(token)

        # Keyword RES
        elif atual == "R":
            self.estadoComandoR(token)

        # Identificadores de Memória são compostos de letras maíusculas
        elif atual.isalpha() and atual.isupper():
            self.estadoComandoMemoria(token)
        else:
            self.estadoErro(token)

    def estadoNumero(self, token: Token):
        # Define o tipo do Token como NUMERO_INTEIRO
        token.tipo = TipoToken.NUMERO_INTEIRO
        # Adiciona o valor atual ao valor do Token
        token.valor += self.get_atual()

        self.avancar()

        if self.get_atual() in NUMEROS_VALIDOS:
            self.estadoNumero(token)
        elif self.get_atual() == SEPARADOR_DECIMAL:
            self.estadoPonto(token)
        else:
            self.transicoesFixas(token)

    def estadoPonto(self, token: Token):
        """Estado para '.' logo depois da parte inteira do número.
        Não é um estado final. Deve ter mais números depois do '.' para ser válido"""

        # Muda o tipo do Token para NUMERO_REAL
        token.tipo = TipoToken.NUMERO_REAL
        # Adiciona o valor da posição atual ao valor do token
        token.valor += self.get_atual()

        self.avancar()

        if self.get_atual() in NUMEROS_VALIDOS:
            self.estadoDecimal(token)
        else:
            self.estadoErro(token)

    def estadoDecimal(self, token: Token):
        """Estado para números com casas decimais.
        A parte inteira do número ja deve estar no Token"""

        # Muda o tipo do Token para NUMERO_REAL
        token.tipo = TipoToken.NUMERO_REAL
        # Adiciona o valor da posição atual ao valor do token
        token.valor += self.get_atual()

        self.avancar()

        if self.get_atual() in NUMEROS_VALIDOS:
            self.estadoDecimal(token)
        else:
            self.transicoesFixas(token)

    def estadoOperador(self, token: Token):
        token.tipo = TipoToken.OPERADOR
        token.valor = self.get_atual()
        self.avancar()

        if self.get_atual() == "/":
            self.estadoDivisaoInteiro(token)
        else:
            self.transicoesFixas(token)

    def estadoDivisaoInteiro(self, token: Token):
        token.tipo = TipoToken.OPERADOR
        token.valor += self.get_atual()
        self.avancar()

        self.transicoesFixas(token)

    def estadoParenteseEsq(self, token: Token):
        token.tipo = TipoToken.PARENTESE_ESQ
        token.valor = self.get_atual()
        self.avancar()

        if self.get_atual() == SEPARADOR_TOKEN:
            self.avancar()
            self.estadoInicial(token)
        elif self.get_atual() == SEPARADOR_EXPRESSAO:
            self.estadoFinal(token)
        else:
            # Qualquer coisa pode vir depois de um PARENTESE_ESQ
            self.estadoInicial(token)

    def estadoParenteseDir(self, token: Token):
        token.tipo = TipoToken.PARENTESE_DIR
        token.valor = self.get_atual()
        self.avancar()

        self.transicoesFixas(token)

    def estadoComandoR(self, token: Token):
        """Estado para primeira letra da keyword RES"""
        token.tipo = TipoToken.MEMORIA
        token.valor += self.get_atual()
        self.avancar()

        if self.get_atual() == "E":
            self.estadoComandoE(token)
        elif self.get_atual().isalpha() and self.get_atual().isupper():
            self.estadoComandoMemoria(token)
        else:
            self.transicoesFixas(token)

    def estadoComandoE(self, token: Token):
        """Estado para segunda letra da keyword RES"""

        token.tipo = TipoToken.MEMORIA
        token.valor += self.get_atual()
        self.avancar()

        if self.get_atual() == "S":
            self.estadoComandoS(token)
        elif self.get_atual().isalpha() and self.get_atual().isupper():
            self.estadoComandoMemoria(token)
        else:
            self.transicoesFixas(token)

    def estadoComandoS(self, token: Token):
        """Estado para terceira e última letra da keyword RES"""
        token.tipo = TipoToken.KEYWORD
        token.valor += self.get_atual()
        self.avancar()

        if self.get_atual().isalpha() and self.get_atual().isupper():
            self.estadoComandoMemoria(token)
        else:
            self.transicoesFixas(token)

    def estadoComandoMemoria(self, token: Token):
        """Estado para comandos de memória. Devem ser letras maiúsculas"""
        token.tipo = TipoToken.MEMORIA
        token.valor += self.get_atual()
        self.avancar()

        if self.get_atual().isalpha() and self.get_atual().isupper():
            self.estadoComandoMemoria(token)
        else:
            self.transicoesFixas(token)

    def estadoFinal(self, token: Token):
        self.tokens_linha_atual.append(token)
        self.matriz_tokens.append(self.tokens_linha_atual)

    def estadoErro(self, token: Token):
        raise ErroTokenInvalido(f"{token.valor}", token.linha, token.coluna)

    def transicoesFixas(self, token: Token):
        """Função auxilar para transições de estado presente em quase todos os estados. Não é um estado."""
        if self.is_fim_token():
            self.estadoInicial(token)
        elif self.get_atual() == SEPARADOR_EXPRESSAO:
            self.estadoFinal(token)
        else:
            self.estadoErro(token)
<<<<<<< HEAD


if __name__ == "__main__":
    analisador = AnalisadorLexico()

    analisador.parseExpressao(
        "1 11 1.1 * // / + - % ^ RES MEM TESTE GAMER ( ) () (11 1 +) *\n",
        1,
    )
    analisador.parseExpressao(
        "LEGAL - + * 1.1 - (1 MEM -) + (RES) R RE RER (NOME) RA (REA) RESA RES 1 +\n",
        2,
    )
    for i in analisador.matriz_tokens:
        print(f"\n ---nova linha---\n")
        for j in i:
            print(j)
=======
>>>>>>> main
