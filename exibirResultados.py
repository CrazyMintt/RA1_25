'''
Equipe:
Bruno Betiatto Alves @Brunobetiatto
Bruno Himovski Opuszka Machado Dutra @CrazyMintt
Leonardo Saito @Leosaito632
Vitor Nicoletti @vitorNicoletti

GRUPO: RA1-25
'''
def exibirResultados(resultados, linha):
    for i, resultado in enumerate(resultados, start=1):
        try:
            print(f"Linha {linha}: {resultado:.1f}")
        except:
            print(f"Linha {linha}: {resultado}")
