- [ ] Separação de Token
    - Obrigatoriamente separado por espaço (` `)?
    - 123+ -> 2 tokens (123, +) ou erro?
- [ ] Formatação de Float
    - O que fazer com numero terminado com `.` (tipo `123.`)?
        - Lancar erro?             <-- Acho que sim
        - Adicionar um 0 no final? <-- Acho que não é papel do analisador lexico.

- [ ] Autômato Finito Determinístico
    - Pode ter um Loop principal que faz a transição para outros estados?
        - Os estados identificam um token ou chamam outro estado
            - Tipo o `estadoNumero` que pode retornar um `Token` ou chama o `estadoDecimal`
        - Os estados retornam um `Token` pro loop principal, que adiciona a uma lista e faz a transição para outros estados ou encerra.

- [ ] `estadoParentese`
    - Um estado para cada parentese?
    - Unificar os tipos?
        - O `estadoParentese` atualmente pode retornar um token do tipo `PARENTESE_ESQ` ou `PARENTESE_DIR`


