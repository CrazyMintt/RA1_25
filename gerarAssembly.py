from parseExpressao import Token, TipoToken

OPERACOES_DIVISIVAS = ["/", "//", "%"]

class geradorAssembly():
    def __init__(self):
        self.memoria = {}
        self.codigo_assembly = []
        self.data_section = []
        self.current_line = 0
        self.data_counter = 0
        self.tmp_counter = 0
        self.regs_livres_int = [f"R{i}" for i in reversed(range(0, 10))]
        self.regs_livres_float = [f"D{i}" for i in reversed(range(1, 32))]

    def alocar_reg(self, eh_float: bool) -> str:
        pool = self.regs_livres_float if eh_float else self.regs_livres_int
        if not pool:
            raise RuntimeError("Registradores esgotados")
        n = pool.pop()
        return n

    def liberar_reg(self, reg: str):
        if reg.startswith("D"):
            print(self.regs_livres_float)
            self.regs_livres_float.append(reg)
        else:
            print(self.regs_livres_int)
            self.regs_livres_int.append(reg)
    def resolver_parenteses(self, tokens: list[Token]):
        pilha_parentes_abertos = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.tipo == TipoToken.PARENTESE_ESQ:
                pilha_parentes_abertos.append(i)
                i += 1
            elif token.tipo == TipoToken.PARENTESE_DIR:
                i_abertura = pilha_parentes_abertos.pop()
                tokens_in_p = tokens[i_abertura + 1 : i]   # conteúdo entre ( )
                _, pilha = self.gerarAssembly(tokens_in_p)
                tokens[i_abertura : i + 1] = pilha          # substitui ( conteúdo )
                i = i_abertura + len(pilha)                  # reposiciona o índice
            else:
                i += 1
        return tokens
    def gerarAssembly(self, tokens: list[Token]) -> str:
        pilha = []
        tokens = self.resolver_parenteses(tokens)
        for token in tokens:

            if token.linha != self.current_line:
                pilha = []
                self.current_line = token.linha
            if token.tipo == TipoToken.OPERADOR:
                b = pilha.pop()
                a = pilha.pop()
                new_token = self.criar_op_line_assembly(a, b, token)
                pilha.append(new_token)

            elif token.tipo not in (TipoToken.PARENTESE_DIR, TipoToken.PARENTESE_ESQ):
                pilha.append(token)

        assembly  = ".section .data\n"
        assembly += "\n".join(self.data_section)
        assembly += "\n\n.section .text\n.global _start\n_start:\n"
        assembly += "\n".join(self.codigo_assembly)
        assembly += "\nfim:"
        assembly += "\nB fim"
        return assembly,pilha

    def get_assembly_keyword(self, operacao: Token, eh_float: bool) -> str:
        if eh_float:
            mapa = {
                "+":  "VADD.F64",
                "-":  "VSUB.F64",
                "*":  "VMUL.F64",
                "/":  "VDIV.F64",
                "//": "VDIV.F64",
                "%":  "VDIV.F64",
                "^":  "VMUL.F64",   # usado só como fallback; o loop trata tudo
            }
        else:
            mapa = {"+": "ADD", "-": "SUB", "*": "MUL","^":"MUL"}

        kw = mapa.get(operacao.valor)
        if kw is None:
            raise ValueError(f"Operador desconhecido: '{operacao.valor}'")
        return kw

    def _criar_label_float(self, valor) -> str:
        label = f"num_{self.data_counter}"
        self.data_counter += 1
        self.data_section.append(f"{label}: .double {valor}")
        return label

    def _is_float(self, token: Token) -> bool:
        if token.tipo == TipoToken.NUMERO_REAL:
            return True
        if token.tipo == TipoToken.MEMORIA:
            reg = self.memoria.get(token.valor)
            return reg is not None and reg.startswith("D")
        return False

    def _define_token_headers(self, token: Token, eh_float: bool):
        header = ""
        reg_usado = None
        if eh_float:
            if token.tipo == TipoToken.NUMERO_INTEIRO:
                token.valor = f"{float(token.valor):.2f}"
            reg_usado = self.alocar_reg(eh_float=True)
            label = self._criar_label_float(token.valor)
            header += f"LDR R12, ={label}\n"
            header += f"VLDR {reg_usado}, [R12]\n"
        elif token.tipo == TipoToken.NUMERO_INTEIRO:
            reg_usado = self.alocar_reg(eh_float=False)
            header += f"MOV {reg_usado}, #{token.valor}\n"
        elif token.tipo == TipoToken.MEMORIA:
            reg_usado = self.memoria.get(token.valor)
            if reg_usado is None:
                reg_usado = self.alocar_reg(eh_float=True)
                label = self._criar_label_float(0.0)
                header += f"LDR R12, ={label}\n"
                header += f"VLDR {reg_usado}, [R12]\n"
        return header, reg_usado

    def _op_creates_floats(self, operacao) -> bool:
        return operacao.valor in OPERACOES_DIVISIVAS

    def create_op_headers(self, a: Token, b: Token, operacao: Token):
        eh_float = self._is_float(a) or self._is_float(b) or self._op_creates_floats(operacao)
        header_a, reg_a = self._define_token_headers(a, eh_float)
        header_b, reg_b = self._define_token_headers(b, eh_float)
        return header_a + header_b, reg_a, reg_b, eh_float

    def convert_64b_to_int(self, reg):
        linhas = []
        linhas.append(f"vcvt.s32.f64 s0, {reg}")
        self.liberar_reg(reg)
        reg_saida = self.alocar_reg(eh_float=False)
        linhas.append(f"vmov {reg_saida}, s0")
        return linhas, reg_saida
    def _criar_pow_loop(self,kw,reg_a,reg_b,reg_resultado,eh_float):
        before_op = []
        if eh_float:
            label_um = self._criar_label_float("1.00")
            before_op.append(f"LDR R12, ={label_um}")
            before_op.append(f"VLDR {reg_resultado}, [R12]")
        else:
            before_op.append(f"MOV {reg_resultado}, #1")
        # Loop de multiplicação (label único por operação)
        loop_id  = self.tmp_counter
        lbl_loop = f"pow_loop_{loop_id}"
        lbl_end  = f"pow_end_{loop_id}"
        before_op.append(f"{lbl_loop}:")
        before_op.append(f"CMP {reg_b}, #0")
        before_op.append(f"BEQ {lbl_end}")
        before_op.append(f"{kw} {reg_resultado}, {reg_resultado}, {reg_a}")
        before_op.append(f"SUB {reg_b}, {reg_b}, #1")
        before_op.append(f"B {lbl_loop}")
        before_op.append(f"{lbl_end}:")
        return before_op
    def criar_op_line_assembly(self, a: Token, b: Token, operacao: Token) -> Token:
        header, reg_a, reg_b, eh_float = self.create_op_headers(a, b, operacao)
        kw = self.get_assembly_keyword(operacao, eh_float)

        reg_resultado = self.alocar_reg(eh_float=eh_float)

        # ── before_op: lógica pré-operação ──────────────────────────────────
        before_op = []
        if operacao.valor == "^":
            before_op.extend(self._criar_pow_loop(kw,reg_a,reg_b,reg_resultado,eh_float))
            linha = ""
        else:
            # ── linha principal (vazia para ^, pois o loop já fez tudo) ─────────
            linha = f"{kw} {reg_resultado}, {reg_a}, {reg_b}"

        # ── after_op: conversões pós-operação ───────────────────────────────
        after_op = []
        if operacao.valor == "//" or operacao.valor == "%":
            linhas_assembly, reg_resultado = self.convert_64b_to_int(reg_resultado)
            after_op.extend(linhas_assembly)

        if operacao.valor == "%":
            linhas_assembly_a, reg_a = self.convert_64b_to_int(reg_a)
            after_op.extend(linhas_assembly_a)
            linhas_assembly_b, reg_b = self.convert_64b_to_int(reg_b)
            after_op.extend(linhas_assembly_b)
            reg_saida = self.alocar_reg(eh_float=False)
            after_op.append(f"MUL {reg_saida}, {reg_resultado}, {reg_b}")
            after_op.append(f"SUB {reg_saida}, {reg_a}, {reg_saida}")
            self.liberar_reg(reg_resultado)
            reg_resultado = reg_saida

        # ── libera registradores de entrada ─────────────────────────────────
        self.liberar_reg(reg_a)
        self.liberar_reg(reg_b)

        # ── registra resultado como token temporário ─────────────────────────
        tmp_key = f"tmp_{self.tmp_counter}"
        self.tmp_counter += 1
        self.memoria[tmp_key] = reg_resultado

        self.codigo_assembly.append(header)
        self.codigo_assembly.extend(before_op)   # ← before_op emitido aqui
        self.codigo_assembly.append(linha)
        self.codigo_assembly.extend(after_op)

        return Token(TipoToken.MEMORIA, tmp_key, self.current_line, operacao.coluna)


# ── Testes ───────────────────────────────────────────────────────────────────

print("==== TESTE INTEIRO ====\n")
tokens_int = [
    Token(TipoToken.NUMERO_INTEIRO, "3", 1, 1),
    Token(TipoToken.NUMERO_INTEIRO, "5", 1, 3),
    Token(TipoToken.OPERADOR, "+", 1, 5),
    Token(TipoToken.NUMERO_INTEIRO, "2", 1, 7),
    Token(TipoToken.OPERADOR, "*", 1, 9),
]
gerador = geradorAssembly()
print(gerador.gerarAssembly(tokens_int))

print("\n==== TESTE POTENCIA ====\n")
tokens_pow = [
    Token(TipoToken.NUMERO_INTEIRO, "2", 1, 1),
    Token(TipoToken.NUMERO_INTEIRO, "3", 1, 3),
    Token(TipoToken.OPERADOR, "^", 1, 5),
]
gerador = geradorAssembly()
print(gerador.gerarAssembly(tokens_pow))

print("\n==== TESTE RESTO ====\n")
tokens_mod = [
    Token(TipoToken.NUMERO_INTEIRO, "10", 1, 1),
    Token(TipoToken.PARENTESE_ESQ, "(", 1, 3),
    Token(TipoToken.NUMERO_INTEIRO, "3",  1, 4),
    Token(TipoToken.NUMERO_INTEIRO, "6",  1, 5),
    Token(TipoToken.OPERADOR, "+", 1, 9),
    Token(TipoToken.PARENTESE_DIR, ")", 1, 6),
    Token(TipoToken.OPERADOR, "+", 1, 9),
]
gerador = geradorAssembly()
print(gerador.gerarAssembly(tokens_mod))