from parseExpressao import AnalisadorLexico
from executarExpressao import executarExpressao, _interpretador_global

def testar_cenario(nome, expressoes_e_esperados):
    print(f"=== Testando Cenário: {nome} ===")
    # Resetar o interpretador para cada cenário
    _interpretador_global.memoria = {}
    _interpretador_global.historico = []
    
    sucesso = True
    for i, (expr, esperado) in enumerate(expressoes_e_esperados):
        try:
            analisador = AnalisadorLexico(expr)
            tokens = analisador.parseExpressao()
            resultado = executarExpressao(tokens)
            
            if abs(resultado - esperado) < 1e-6:
                print(f"  Linha {i+1}: '{expr}' -> {resultado} (OK)")
            else:
                print(f"  Linha {i+1}: '{expr}' -> {resultado} (ERRO! Esperado: {esperado})")
                sucesso = False
        except Exception as e:
            print(f"  Linha {i+1}: '{expr}' -> EXCEÇÃO: {e}")
            sucesso = False
    
    print(f"Resultado Final: {'SUCESSO' if sucesso else 'FALHA'}")
    print("-" * 40)

if __name__ == "__main__":
    # 1. Operações Básicas
    testar_cenario("Aritmética Básica", [
        ("(3.14 2.0 +)", 5.14),
        ("(10 2 *)", 20.0),
        ("(10 3 /)", 10/3),
        ("(10 3 //)", 3.0),
        ("(10 3 %)", 1.0),
        ("(2 3 ^)", 8.0)
    ])

    # 2. Memória (V MEM) e (MEM)
    testar_cenario("Gerenciamento de Memória", [
        ("(10.5 CONTADOR)", 10.5), # Armazena 10.5 em CONTADOR
        ("(5.0 CONTADOR +)", 15.5), # (10.5 + 5.0) -> 15.5 (CONTADOR recuperado)
        ("(X)", 0.0),              # X não inicializado deve retornar 0.0
        ("(20 X)", 20.0),          # Armazena 20 em X
        ("(X X +)", 40.0)          # 20 + 20 = 40
    ])

    # 3. Histórico (N RES)
    testar_cenario("Histórico de Resultados", [
        ("(10 20 +)", 30.0),   # Linha 0: 30
        ("(5 2 *)", 10.0),     # Linha 1: 10
        ("(0 RES)", 10.0),     # Resultado da última linha (índice 0)
        ("(1 RES)", 30.0),     # Resultado da penúltima linha (índice 1)
        ("(0 RES 1 RES +)", 40.0) # (10 + 30) = 40
    ])

    # 4. Expressões Aninhadas
    testar_cenario("Expressões Aninhadas", [
        ("((1.5 2.0 *) (3.0 4.0 *) /)", (1.5*2.0)/(3.0*4.0)), # (3.0 / 12.0) = 0.25
        ("(A (C D *) +)", 0.0) # A=0, C=0, D=0 -> result 0.0
    ])
