import unittest
from parseExpressao import AnalisadorLexico
from executarExpressao import criarInterpretador, executarExpressao


def _parse(expressao: str):
    analisador = AnalisadorLexico()
    analisador.parseExpressao(expressao)
    return analisador.matriz_tokens[-1]

def _executar(expressao: str, interpretador=None):
    if interpretador is None:
        interpretador = criarInterpretador()
    return executarExpressao(_parse(expressao), interpretador)

def _sequencia(expressoes: list[str]) -> list[float]:
    interpretador = criarInterpretador()
    return [_executar(e, interpretador) for e in expressoes]


class TesteOperacoes(unittest.TestCase):

    def test_adicao(self):
        self.assertAlmostEqual(_executar("(3.0 4.0 +)"), 7.0)

    def test_subtracao(self):
        self.assertAlmostEqual(_executar("(10.0 4.0 -)"), 6.0)

    def test_multiplicacao(self):
        self.assertAlmostEqual(_executar("(3.0 4.0 *)"), 12.0)

    def test_divisao_real(self):
        self.assertAlmostEqual(_executar("(15.0 4.0 /)"), 3.75)

    def test_divisao_inteira(self):
        self.assertAlmostEqual(_executar("(17.0 5.0 //)"), 3.0)

    def test_resto(self):
        self.assertAlmostEqual(_executar("(17.0 5.0 %)"), 2.0)

    def test_potenciacao(self):
        self.assertAlmostEqual(_executar("(2.0 8.0 ^)"), 256.0)

    def test_divisao_por_zero(self):
        with self.assertRaises(Exception) as ctx:
            _executar("(5.0 0.0 /)")
        self.assertIn("Divisão por zero", str(ctx.exception))

    def test_divisao_inteira_por_zero(self):
        with self.assertRaises(Exception) as ctx:
            _executar("(5.0 0.0 //)")
        self.assertIn("Divisão inteira por zero", str(ctx.exception))

    def test_resto_por_zero(self):
        with self.assertRaises(Exception) as ctx:
            _executar("(5.0 0.0 %)")
        self.assertIn("Resto da divisão por zero", str(ctx.exception))


class TesteAninhamento(unittest.TestCase):

    def test_dois_niveis(self):
        # (3+2) * (4-1) = 15
        self.assertAlmostEqual(_executar("((3.0 2.0 +) (4.0 1.0 -) *)"), 15.0)

    def test_tres_niveis(self):
        # ((2*3) + 4) / 2 = 5
        self.assertAlmostEqual(_executar("(((2.0 3.0 *) 4.0 +) 2.0 /)"), 5.0)

    def test_subexpressao_como_expoente(self):
        # (10/2) ^ (3+1) = 625
        self.assertAlmostEqual(_executar("((10.0 2.0 /) (3.0 1.0 +) ^)"), 625.0)


class TesteMemoria(unittest.TestCase):

    def test_atribuicao_e_leitura(self):
        rs = _sequencia(["(7.5 TOTAL)", "(TOTAL 2.0 +)"])
        self.assertAlmostEqual(rs[0], 7.5)
        self.assertAlmostEqual(rs[1], 9.5)

    def test_variavel_nao_inicializada_retorna_zero(self):
        self.assertAlmostEqual(_executar("(NAODEFINIDA)"), 0.0)

    def test_leitura_isolada_nao_sobrescreve(self):
        # (BASE) com parênteses próprios deve ler, não atribuir
        rs = _sequencia(["(100.0 BASE)", "((2.0 3.0 ^) (BASE) -)"])
        self.assertAlmostEqual(rs[1], 8.0 - 100.0)

    def test_atribuicao_via_subexpressao(self):
        rs = _sequencia(["((2.0 3.0 *) PARCIAL)", "(PARCIAL)"])
        self.assertAlmostEqual(rs[1], 6.0)

    def test_escopo_independente(self):
        i1, i2 = criarInterpretador(), criarInterpretador()
        _executar("(99.0 X)", i1)
        self.assertAlmostEqual(_executar("(X)", i2), 0.0)


class TesteRES(unittest.TestCase):

    def test_linha_anterior(self):
        rs = _sequencia(["(3.0 4.0 +)", "(1 RES)"])
        self.assertAlmostEqual(rs[1], 7.0)

    def test_duas_linhas_atras(self):
        rs = _sequencia(["(10.0 2.0 /)", "(3.0 3.0 *)", "(2 RES)"])
        self.assertAlmostEqual(rs[2], 5.0)

    def test_res_em_expressao(self):
        rs = _sequencia(["(5.0 2.0 /)", "((1 RES) 2.0 *)"])
        self.assertAlmostEqual(rs[1], 5.0)

    def test_n_zero_invalido(self):
        with self.assertRaises(Exception) as ctx:
            _sequencia(["(1.0 1.0 +)", "(0 RES)"])
        self.assertIn("RES exige N >= 1", str(ctx.exception))

    def test_sem_historico(self):
        with self.assertRaises(Exception) as ctx:
            _sequencia(["(1 RES)"])
        self.assertIn("só existem 0 linha(s)", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)