from gerarAssembly import geradorAssembly
from parseExpressao import TipoToken, Token

# ── Testes ───────────────────────────────────────────────────────────────────
def rodar_teste(nome, matriz_tokens):
    print(f"\n{'='*60}")
    print(f"  {nome}")
    print('='*60)
    gerador = geradorAssembly()
    assembly = gerador.gerarAssembly(matriz_tokens)
    print(assembly)

# ── Testes RES com parênteses corretos ──────────────────────────────────────

rodar_teste("RES simples: linha0 = 3+2, linha1 = (1 RES) → x", [
    [   # linha 0: (3 + 2)
        Token(TipoToken.PARENTESE_ESQ,  "(", 1, 1),
        Token(TipoToken.NUMERO_INTEIRO, "3", 1, 2),
        Token(TipoToken.NUMERO_INTEIRO, "2", 1, 4),
        Token(TipoToken.OPERADOR,       "+", 1, 6),
        Token(TipoToken.PARENTESE_DIR,  ")", 1, 7),
    ],
    [   # linha 1: (1 RES) → x
        Token(TipoToken.PARENTESE_ESQ,  "(", 2, 1),
        Token(TipoToken.NUMERO_INTEIRO, "1", 2, 2),
        Token(TipoToken.KEYWORD,        "RES", 2, 4),
        Token(TipoToken.PARENTESE_DIR,  ")", 2, 5),
        Token(TipoToken.MEMORIA,        "x", 2, 7),
    ]
])

rodar_teste("RES 2 linhas acima: linha0=(4*2), linha1=(10 → y), linha2=(2 RES) → z", [
    [   # linha 0: (4 * 2)
        Token(TipoToken.PARENTESE_ESQ,  "(", 1, 1),
        Token(TipoToken.NUMERO_INTEIRO, "4", 1, 2),
        Token(TipoToken.NUMERO_INTEIRO, "2", 1, 4),
        Token(TipoToken.OPERADOR,       "*", 1, 6),
        Token(TipoToken.PARENTESE_DIR,  ")", 1, 7),
    ],
    [   # linha 1: 10 → y
        Token(TipoToken.NUMERO_INTEIRO, "10", 2, 1),
        Token(TipoToken.MEMORIA,        "y",  2, 4),
    ],
    [   # linha 2: (2 RES) → z
        Token(TipoToken.PARENTESE_ESQ,  "(", 3, 1),
        Token(TipoToken.NUMERO_INTEIRO, "2", 3, 2),
        Token(TipoToken.KEYWORD,        "RES", 3, 4),
        Token(TipoToken.PARENTESE_DIR,  ")", 3, 5),
        Token(TipoToken.MEMORIA,        "z", 3, 7),
    ]
])

rodar_teste("RES em expressão: linha0=(3.0+1.0), linha1=((1 RES) + 5) → x", [
    [   # linha 0: (3.0 + 1.0)
        Token(TipoToken.PARENTESE_ESQ, "(", 1, 1),
        Token(TipoToken.NUMERO_REAL,   "3.0", 1, 2),
        Token(TipoToken.NUMERO_REAL,   "1.0", 1, 6),
        Token(TipoToken.OPERADOR,      "+",   1, 10),
        Token(TipoToken.PARENTESE_DIR, ")", 1, 11),
    ],
    [   # linha 1: ((1 RES) + 5) → x
        Token(TipoToken.PARENTESE_ESQ,  "(", 2, 1),
        Token(TipoToken.PARENTESE_ESQ,  "(", 2, 2),
        Token(TipoToken.NUMERO_INTEIRO, "1",   2, 3),
        Token(TipoToken.KEYWORD,        "RES", 2, 5),
        Token(TipoToken.PARENTESE_DIR,  ")", 2, 8),
        Token(TipoToken.NUMERO_INTEIRO, "5",   2, 10),
        Token(TipoToken.OPERADOR,       "+",   2, 12),
        Token(TipoToken.PARENTESE_DIR,  ")", 2, 13),
        Token(TipoToken.MEMORIA,        "x",   2, 15),
    ]
])

rodar_teste("RES duas vezes: linha0=(6*7), linha1=((1 RES) + (1 RES)) → x", [
    [   # linha 0: (6 * 7)
        Token(TipoToken.PARENTESE_ESQ,  "(", 1, 1),
        Token(TipoToken.NUMERO_INTEIRO, "6", 1, 2),
        Token(TipoToken.NUMERO_INTEIRO, "7", 1, 4),
        Token(TipoToken.OPERADOR,       "*", 1, 6),
        Token(TipoToken.PARENTESE_DIR,  ")", 1, 7),
    ],
    [   # linha 1: ((1 RES) + (1 RES)) → x
        Token(TipoToken.PARENTESE_ESQ,  "(", 2, 1),
        Token(TipoToken.PARENTESE_ESQ,  "(", 2, 2),
        Token(TipoToken.NUMERO_INTEIRO, "1",   2, 3),
        Token(TipoToken.KEYWORD,        "RES", 2, 5),
        Token(TipoToken.PARENTESE_DIR,  ")", 2, 8),
        Token(TipoToken.PARENTESE_ESQ,  "(", 2, 10),
        Token(TipoToken.NUMERO_INTEIRO, "1",   2, 11),
        Token(TipoToken.KEYWORD,        "RES", 2, 13),
        Token(TipoToken.PARENTESE_DIR,  ")", 2, 16),
        Token(TipoToken.OPERADOR,       "+",   2, 18),
        Token(TipoToken.PARENTESE_DIR,  ")", 2, 19),
        Token(TipoToken.MEMORIA,        "x",   2, 21),
    ]
])

rodar_teste("RES float: linha0=(2.5*2.0), linha1=(1 RES) → x", [
    [   # linha 0: (2.5 * 2.0)
        Token(TipoToken.PARENTESE_ESQ, "(", 1, 1),
        Token(TipoToken.NUMERO_REAL,   "2.5", 1, 2),
        Token(TipoToken.NUMERO_REAL,   "2.0", 1, 6),
        Token(TipoToken.OPERADOR,      "*",   1, 10),
        Token(TipoToken.PARENTESE_DIR, ")", 1, 11),
    ],
    [   # linha 1: (1 RES) → x
        Token(TipoToken.PARENTESE_ESQ,  "(", 2, 1),
        Token(TipoToken.NUMERO_INTEIRO, "1",   2, 2),
        Token(TipoToken.KEYWORD,        "RES", 2, 4),
        Token(TipoToken.PARENTESE_DIR,  ")", 2, 7),
        Token(TipoToken.MEMORIA,        "x",   2, 9),
    ]
])

# ── Teste novo: (3 (2 VAR) +) ────────────────────────────────────────────────
# Expressão: resultado = 3 + VAR, onde VAR recebe 2 na mesma linha (inner parens)
# Ou seja: (2 → VAR) calcula o inner, depois (3 + VAR) no outer

rodar_teste("Expressão (3 (2 VAR) +): atribui 2 a VAR e soma com 3", [
    [
        Token(TipoToken.PARENTESE_ESQ,  "(", 1, 1),
        Token(TipoToken.NUMERO_INTEIRO, "3", 1, 2),
        Token(TipoToken.PARENTESE_ESQ,  "(", 1, 4),
        Token(TipoToken.NUMERO_INTEIRO, "2",   1, 5),
        Token(TipoToken.MEMORIA,        "VAR", 1, 7),
        Token(TipoToken.PARENTESE_DIR,  ")", 1, 10),
        Token(TipoToken.OPERADOR,       "+", 1, 12),
        Token(TipoToken.PARENTESE_DIR,  ")", 1, 13),
    ]
])