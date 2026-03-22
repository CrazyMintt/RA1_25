def exibirResultados(resultados):
    #exibe os resultados das expressões processadas, formatando para 1 casa decimal.
    print("\nResultados das expressões:\n")

    for i, resultado in enumerate(resultados, start=1):
        try:
            print(f"Linha {i}: {resultado:.1f}")
        except:
            print(f"Linha {i}: {resultado}")
