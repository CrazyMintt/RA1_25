'''
Equipe:
Bruno Betiatto Alves @Brunobetiatto
Bruno Himovski Opuszka Machado Dutra @CrazyMintt
Leonardo Saito @Leosaito632
Vitor Nicoletti @vitorNicoletti

GRUPO: RA1-25
'''

def exibirResultados(resultados, linha):
    for r in resultados:
        # Validação de integridade
        eh_numero = isinstance(r, (int, float))
        tem_conteudo = r is not None and str(r).strip() != ""

        if eh_numero:
            truncado = int(r * 10) / 10
            print(f"Linha {linha}: {truncado:.1f}")
        elif tem_conteudo:
            print(f"[Erro]")
        else:
            print(f"[Vazio ou Invalido]")

def realizar_teste():
    # Dados para validar: float, int, string, vazio, None
    casos = [15.0/4.0, 10, "Erro Sintatico", "", None]
    
    print("--- Validacao de Dados ---")
    exibirResultados(casos, 1)

if __name__ == "__main__":
    realizar_teste()