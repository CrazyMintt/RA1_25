from parseExpressao import AnalisadorLexico, TipoToken
def testar_afd(expressao):
   print(f"Testando: {expressao}")
   try:
       analisador = AnalisadorLexico(expressao)
       tokens = analisador.parseExpressao()
       for t in tokens:
           print(f"  {t}")
       print("  Resultado: SUCESSO")
   except Exception as e:
       print(f"  Resultado: ERRO - {e}")
   print("-" * 30)
if __name__ == "__main__":
    testes_validos = [
        "(3.14 2.0 +)",
        "(5 RES)",
        "(10.5 CONTADOR)", # Usei CONTADOR (maiusculo) para evitar erro conhecido
        "((A B *) (D E *) /)",
        "(10 20 //)",
        "(7 3 %)",
        "(2 3 ^)"
    ]

    testes_invalidos = [
        "(3.14 2.0 &)",      # Caractere invalido &
        "3.14.5",            # Numero malformado
        "(3.14 2.0",         # Parenteses desbalanceados
        "3,45",              # Virgula nao permitida
        "(10.5 CONTADOr)"    # Minuscula (deve falhar conforme implementacao atual)
    ]

    print("=== TESTES VALIDOS ===")
    for t in testes_validos:
        testar_afd(t)

    print("\n=== TESTES INVALIDOS ===")
    for t in testes_invalidos:
        testar_afd(t)