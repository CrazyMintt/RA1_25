'''
Equipe:
Bruno Betiatto Alves @Brunobetiatto
Bruno Himovski Opuszka Machado Dutra @CrazyMintt
Leonardo Saito @Leosaito632
Vitor Nicoletti @vitorNicoletti

GRUPO: RA1-25
'''
def exibirResultados(resultados):
    #exibe os resultados das expressões processadas, formatando para 1 casa decimal.
    print("\nResultados das expressões:\n")

    for i, resultado in enumerate(resultados, start=1):
        try:
            print(f"Linha {i}: {resultado:.1f}")
        except:
            print(f"Linha {i}: {resultado}")
