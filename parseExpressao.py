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
    tokens_linha_atual: list[Token]  # Tokens da expressao atual
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

    def parseExpressao(self, expressao: str):
        """
        Função chamada para cada linha (expressão) que será analisada.
        A `expressão` deve ser uma string de caracteres válidos,
        com quebra de linha `\\n` no final para delimitar o fim da expressão
        """

        # Prepara o estado para a nova linha
        self.expressao = expressao
        self.linha_atual += 1
        self.coluna_atual = 0
        self.tokens_linha_atual = []

        self.estadoInicial()
        return self.tokens_linha_atual

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
            token.valor = atual  # Adiciona o caractere onde o erro ocorreu
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


def testes_analisador_lexico():
    print("TESTES DO ANALISADOR LEXICO")
    analisador = AnalisadorLexico()

    print("Testes com Tokens Válidos")
    expr_valida_1 = analisador.parseExpressao(
        "1 2 3.4 + - * / // ^ % R RE RES REA MEM\n"
    )
    print("\n".join([str(t) for t in expr_valida_1]))
    print("\n---\n")
    expr_valida_2 = analisador.parseExpressao(
        "TESTE (MEM) (3 RES) ((1 4 +) (1 3 -) *)\n"
    )
    print("\n".join([str(t) for t in expr_valida_2]))

    print("\nTestes com Erros esperados\n")
    try:
        expr_invalida_1 = analisador.parseExpressao("10 3 + 1.1.\n")
    except ErroTokenInvalido as e:
        print(f"Erro esperado encontrado: {e}")
    try:
        expr_invalida_2 = analisador.parseExpressao("4 RES 1 MEM &\n")
    except ErroTokenInvalido as e:
        print(f"Erro esperado encontrado: {e}")
    try:
        expr_invalida_3 = analisador.parseExpressao("1.1 2 + VAR")
    except ErroTokenInvalido as e:
        print(f"Erro esperado encontrado: {e}")


if __name__ == "__main__":
    testes_analisador_lexico()
