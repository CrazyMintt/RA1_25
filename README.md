# Referência para documentação
[https://frankalcantara.com/lf/fase12026-1.html](https://frankalcantara.com/lf/fase12026-1.html)

---

Instituição: Pontifícia Universidade Católica do Paraná

Professor: Frank Coelho de Alcantara

Grupo: RA1 25

Alunos:
- Bruno Betiatto Alves - [Brunobetiatto](https://github.com/Brunobetiatto)
- Bruno Himovski Opuszka Machado Dutra - [CrazyMintt](https://github.com/CrazyMintt)
- Leonardo Saito - [Leosaito632](https://github.com/Leosaito632)
- Vitor Nicoletti - [vitorNicoletti](https://github.com/vitorNicoletti)

---

# Execução do código

## Pré-requisitos
- Interpretador da Linguagem [Python](https://www.python.org/)
- Sistema de controle de versões [Git](https://git-scm.com/)

## Como executar
1. Fazer cópia do repositório com o comando `git clone https://github.com/CrazyMintt/RA1_25.git`
2. Executar o arquivo `main.py` passando o arquivo `.txt` contendo as expressões como parâmetro
    - Exemplo: `python main.py Teste1.txt`
3. O código irá gerar um arquivo com o código `assembly` responsável por resolver as expressões.

## Testes

1. Analisador Lexico

Os testes do Analisador Lexico foram escritos com a biblioteca `unittest` do `python`, e cobrem casos de expressões válidas e inválidas.

Os testes podem ser executados com `python test_analisador_lexico.py`. Exemplo de uma execução válida:

```sh
$ python test_analisador_lexico.py
......
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

Para obter mais detalhes, é possível executar o mesmo comando usando a opção `-v`. (`python test_analisado_lexico.py -v`). Exemplo de uma execução válida:
```sh
$ python test_analisado_lexico.py -v
test_invalida_caractere_especial (__main__.TestAnalisadorLexico.test_invalida_caractere_especial)
Caractere '&' não pertence ao alfabeto da linguagem. ... ok
test_invalida_letra_minuscula (__main__.TestAnalisadorLexico.test_invalida_letra_minuscula)
Letras minúsculas não são reconhecidas pelo analisador. ... ok
test_invalida_numero_real_mal_formado (__main__.TestAnalisadorLexico.test_invalida_numero_real_mal_formado)
Dois pontos decimais no mesmo número são inválidos. ... ok
test_valida_expressao_aninhada_com_parenteses (__main__.TestAnalisadorLexico.test_valida_expressao_aninhada_com_parenteses)
Expressão aninhada com parênteses e identificador de memória. ... ok
test_valida_expressao_com_real_e_memoria (__main__.TestAnalisadorLexico.test_valida_expressao_com_real_e_memoria)
Expressão misturando número real, keyword RES e operador. ... ok
test_valida_expressao_simples (__main__.TestAnalisadorLexico.test_valida_expressao_simples)
Soma de dois inteiros em notação polonesa reversa. ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

2. `executarExpressao.py`

As funções do arquivo `executarExpressao.py` tem o propósito de **testar as expressões e validar o resultado do código `assembly` gerado**. Os calculos realizados aqui **não interferem com o código gerado pelo `gerarAssembly.py`**.

