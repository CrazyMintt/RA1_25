"""
Equipe:
Bruno Betiatto Alves @Brunobetiatto
Bruno Himovski Opuszka Machado Dutra @CrazyMintt
Leonardo Saito @Leosaito632
Vitor Nicoletti @vitorNicoletti

GRUPO: RA1-25
"""

import unittest
from parseExpressao import AnalisadorLexico, TipoToken, ErroTokenInvalido


class TestAnalisadorLexico(unittest.TestCase):

    def setUp(self):
        self.analisador = AnalisadorLexico()

    # Expressões válidas

    def test_valida_expressao_simples(self):
        """Soma de dois inteiros em notação polonesa reversa."""
        tokens = self.analisador.parseExpressao("(3 4 +)")
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[1].tipo, TipoToken.NUMERO_INTEIRO)
        self.assertEqual(tokens[2].tipo, TipoToken.NUMERO_INTEIRO)
        self.assertEqual(tokens[3].tipo, TipoToken.OPERADOR)

    def test_valida_expressao_com_real_e_memoria(self):
        """Expressão misturando número real, keyword RES e operador."""
        tokens = self.analisador.parseExpressao("(1.5 RES +)")
        self.assertEqual(tokens[1].tipo, TipoToken.NUMERO_REAL)
        self.assertEqual(tokens[2].tipo, TipoToken.KEYWORD)
        self.assertEqual(tokens[3].tipo, TipoToken.OPERADOR)

    def test_valida_expressao_aninhada_com_parenteses(self):
        """Expressão aninhada com parênteses e identificador de memória."""
        tokens = self.analisador.parseExpressao("(( 1 4 + ) MEM * )")
        self.assertEqual(tokens[0].tipo, TipoToken.PARENTESE_ESQ)
        self.assertEqual(tokens[-1].tipo, TipoToken.PARENTESE_DIR)
        self.assertEqual(tokens[6].tipo, TipoToken.MEMORIA)

    # Expressões inválidas

    def test_invalida_caractere_especial(self):
        """Caractere '&' não pertence ao alfabeto da linguagem."""
        with self.assertRaises(ErroTokenInvalido):
            self.analisador.parseExpressao("((4 RES) (1 MEM) &))")

    def test_invalida_numero_real_mal_formado(self):
        """Dois pontos decimais no mesmo número são inválidos."""
        with self.assertRaises(ErroTokenInvalido):
            self.analisador.parseExpressao("((10 3 +) 1.1.)")

    def test_invalida_letra_minuscula(self):
        """Letras minúsculas não são reconhecidas pelo analisador."""
        with self.assertRaises(ErroTokenInvalido):
            self.analisador.parseExpressao("((1 2 +) res)")


if __name__ == "__main__":
    unittest.main()
