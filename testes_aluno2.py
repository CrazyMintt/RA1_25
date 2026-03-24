from parseExpressao import AnalisadorLexico
from executarExpressao import executarExpressao, _interpretador_global, lidarComParentesesAninhados

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
        ("(10 3 //)", 3.0),
        ("(10 3 %)", 1.0)
    ])

    # 2. Memória
    testar_cenario("Gerenciamento de Memória", [
        ("(10.5 CONTADOR)", 10.5),
        ("(5.0 CONTADOR +)", 15.5)
    ])

    # 3. Histórico (N RES) - Índices Corrigidos
    # L1: 30, L2: 10, L3: 10 (ref L2), L4: 30 (ref L1)
    testar_cenario("Histórico de Resultados", [
        ("(10 20 +)", 30.0),   # Linha 1 -> hist[0] = 30
        ("(5 2 *)", 10.0),     # Linha 2 -> hist[1] = 10
        ("(0 RES)", 10.0),     # Linha 3 -> 0 RES pega hist[1] -> 10. hist[2] = 10
        ("(2 RES)", 30.0),     # Linha 4 -> 2 RES pega hist[0] -> 30. hist[3] = 30
        ("(0 RES 1 RES +)", 40.0) # Linha 5 -> 0 RES(30) + 1 RES(10) -> 40
    ])

    # 4. Parênteses Aninhados (Preparação para Assembly)
    print("=== Testando Tratamento de Parênteses Aninhados ===")
    expr = "((1.5 2.0 *) (3.0 4.0 *) /)"
    analisador = AnalisadorLexico(expr)
    tokens = analisador.parseExpressao()
    tokens_limpos = lidarComParentesesAninhados(tokens)
    print(f"Expressão Original: {expr}")
    print(f"Tokens para Assembly: {[t.valor for t in tokens_limpos]}")
    if "(" not in [t.valor for t in tokens_limpos]:
        print("Resultado: SUCESSO (Parênteses removidos)")
    else:
        print("Resultado: FALHA (Parênteses ainda presentes)")
