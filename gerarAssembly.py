from parseExpressao import Token, TipoToken

OPERACOES_DIVISIVAS = ["/", "//", "%"]

class geradorAssembly():
    def __init__(self):
        self.memoria = {}
        self.codigo_assembly = []
        self.data_section = []
        self.current_line = 0
        self.data_counter = 0
        self.res_counter = 0
        self.tmp_counter = 0
        self.regs_livres_int = [f"R{i}" for i in reversed(range(0, 10))]
        self.regs_livres_float = [f"D{i}" for i in reversed(range(1, 32))]

    def alocar_reg(self, eh_float: bool) -> str:
        pool = self.regs_livres_float if eh_float else self.regs_livres_int
        if not pool:
            raise RuntimeError("Registradores esgotados")
        return pool.pop()

    def liberar_reg(self, reg: str):
        if reg.startswith("D"):
            self.regs_livres_float.append(reg)
        else:
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
                tokens_in_p = tokens[i_abertura + 1: i]
                pilha = self._gerar_linha_assembly(tokens_in_p)

                resultado = []
                for t in pilha:
                    if t.tipo == TipoToken.MEMORIA and not t.valor.startswith("tmp_"):
                        tmp_key = f"tmp_{self.tmp_counter}"
                        self.tmp_counter += 1
                        self.memoria[tmp_key] = self.memoria.get(t.valor)
                        resultado.append(Token(TipoToken.MEMORIA, tmp_key, t.linha, t.coluna))
                    else:
                        resultado.append(t)

                tokens[i_abertura: i + 1] = resultado
                i = i_abertura + len(resultado)
            else:
                i += 1
        return tokens

    def _salvar_valor_a_reg(self, token_origem: Token, reg_destino: str):
        if token_origem.tipo == TipoToken.NUMERO_INTEIRO:
            label = self._criar_label_float(f"{float(token_origem.valor):.2f}")
            self.codigo_assembly.append(f"LDR R12, ={label}")
            self.codigo_assembly.append(f"VLDR {reg_destino}, [R12]")

        elif token_origem.tipo == TipoToken.NUMERO_REAL:
            label = self._criar_label_float(token_origem.valor)
            self.codigo_assembly.append(f"LDR R12, ={label}")
            self.codigo_assembly.append(f"VLDR {reg_destino}, [R12]")

        elif token_origem.tipo == TipoToken.MEMORIA:
            reg_origem = self.memoria.get(token_origem.valor)

            if reg_origem is None:
                label = self._criar_label_float("0.0")
                self.codigo_assembly.append(f"LDR R12, ={label}")
                self.codigo_assembly.append(f"VLDR {reg_destino}, [R12]")

            elif reg_origem.startswith("D"):
                self.codigo_assembly.append(f"VMOV.F64 {reg_destino}, {reg_origem}")

            else:
                self.codigo_assembly.append(f"VMOV  s0, {reg_origem}")
                self.codigo_assembly.append(f"VCVT.F64.S32 {reg_destino}, s0")

        else:
            raise ValueError(f"Tipo inesperado em _salvar_valor_a_reg: {token_origem.tipo}")

    def _gerar_linha_assembly(self, tokens_line):
        pilha = []
        for token in tokens_line:
            if token.tipo == TipoToken.MEMORIA and not token.valor.startswith("tmp_"):
                try:
                    token_atribuir = pilha.pop()
                    reg_var = self.memoria.get(token.valor)
                    if not reg_var or not reg_var.startswith("D"):
                        reg_var = self.alocar_reg(True)
                    self._salvar_valor_a_reg(token_atribuir, reg_var)
                    self.memoria[token.valor] = reg_var
                except IndexError:
                    pass
                pilha.append(token)
            elif token.tipo == TipoToken.KEYWORD:
                if token.valor == "RES":
                    n_tk = pilha.pop()
                    linha_res = self.current_line - int(n_tk.valor)
                    reg_res = self.memoria.get(f"res_linha_{linha_res}")
                    pilha.append(Token(TipoToken.MEMORIA, f"res_linha_{linha_res}", self.current_line))
            elif token.tipo == TipoToken.OPERADOR:
                b = pilha.pop()
                a = pilha.pop()
                new_token = self.criar_op_line_assembly(a, b, token)
                pilha.append(new_token)

            elif token.tipo not in (TipoToken.PARENTESE_DIR, TipoToken.PARENTESE_ESQ):
                pilha.append(token)
        return pilha

    def resolver_RES(self, token_matrix: list[list[Token]]):
        for i, tokens_line in enumerate(token_matrix):
            for j, token in enumerate(tokens_line):
                if token.tipo == TipoToken.KEYWORD and token.valor == "RES":
                    n = None
                    for k in range(j - 1, -1, -1):
                        if tokens_line[k].tipo == TipoToken.NUMERO_INTEIRO:
                            n = int(tokens_line[k].valor)
                            break

                    if n is None:
                        raise ValueError(f"RES na linha {i} sem número antes dele")

                    linha_para_salvar = i - n
                    if linha_para_salvar < 0:
                        raise ValueError(f"RES({n}) na linha {i} aponta para linha negativa")

                    nome_variavel = f"res_linha_{linha_para_salvar}"
                    if not self.memoria.get(nome_variavel):
                        eh_float = self.line_is_float(token_matrix[linha_para_salvar])
                        reg_res = self.alocar_reg(eh_float)
                        self.memoria[nome_variavel] = reg_res
                        token_matrix[linha_para_salvar].append(
                            Token(TipoToken.MEMORIA, nome_variavel, linha_para_salvar, 0)
                        )
        return token_matrix

    def _emitir_print_linha(self, pilha: list):
        if not pilha:
            return
        token_resultado = pilha[-1]
        if token_resultado.tipo != TipoToken.MEMORIA:
            return
        reg = self.memoria.get(token_resultado.valor)
        if reg is None:
            return
        if reg.startswith("D"):
            self.codigo_assembly.append(f"VCVT.S32.F64 s0, {reg}")
            self.codigo_assembly.append(f"VMOV R0, s0")
        else:
            self.codigo_assembly.append(f"MOV R0, {reg}")
        self.codigo_assembly.append("BL __jtag_print_int")

    def _subrotina_jtag(self) -> str:
        return """\
    __jtag_print_int:
        PUSH {R1, R2, R3, R4, R5, R6, LR}
        LDR  R1, =0xFF201000
        CMP  R0, #0
        BGE  __pji_pos
        MOV  R6, #0x2D
        STR  R6, [R1]
        RSB  R0, R0, #0
    __pji_pos:
        CMP  R0, #0
        BNE  __pji_loop
        MOV  R6, #0x30
        STR  R6, [R1]
        B    __pji_nl
    __pji_loop:
        @ divide R0 por 10 sem UDIV (subtração sucessiva)
        MOV  R3, #0
        MOV  R2, R0
    __pji_div:
        CMP  R2, #10
        BLT  __pji_div_end
        SUB  R2, R2, #10
        ADD  R3, R3, #1
        B    __pji_div
    __pji_div_end:
        @ R3 = quociente, R2 = resto
        ADD  R5, R2, #0x30
        PUSH {R5}
        ADD  R4, R4, #1
        MOV  R0, R3
        CMP  R0, #0
        BNE  __pji_loop
        MOV  R3, R4
    __pji_print:
        POP  {R5}
        STR  R5, [R1]
        SUBS R3, R3, #1
        BNE  __pji_print
    __pji_nl:
        MOV  R6, #0x0A
        STR  R6, [R1]
        POP  {R1, R2, R3, R4, R5, R6, LR}
        BX   LR
    """

    def gerarAssembly(self, token_matrix: list[list[Token]]) -> str:
        pilha = []
        token_matrix = self.resolver_RES(token_matrix)
        for i, tokens_line in enumerate(token_matrix):
            tokens_line = self.resolver_parenteses(tokens_line)
            pilha = self._gerar_linha_assembly(tokens_line)  # captura pilha
            self._emitir_print_linha(pilha)                  # print JTAG
            self.current_line += 1
        assembly  = ".section .data\n"
        assembly += "\n".join(self.data_section)
        assembly += "\n\n.section .text\n.global _start\n_start:\n"
        assembly += "\n".join(self.codigo_assembly)
        assembly += "\nfim:\n"
        assembly += "B fim\n"
        assembly += self._subrotina_jtag()                   # sub-rotina no final
        return assembly

    def get_assembly_keyword(self, operacao: Token, eh_float: bool) -> str:
        if eh_float:
            mapa = {
                "+":  "VADD.F64",
                "-":  "VSUB.F64",
                "*":  "VMUL.F64",
                "/":  "VDIV.F64",
                "//": "VDIV.F64",
                "%":  "VDIV.F64",
                "^":  "VMUL.F64",
            }
        else:
            mapa = {"+": "ADD", "-": "SUB", "*": "MUL", "^": "MUL"}

        kw = mapa.get(operacao.valor)
        if kw is None:
            raise ValueError(f"Operador desconhecido: '{operacao.valor}'")
        return kw

    def _criar_label_float(self, valor) -> str:
        label = f"num_{self.data_counter}"
        self.data_counter += 1
        self.data_section.append(f"{label}: .double {valor}")
        return label

    def line_is_float(self, token_list):
        for token in token_list:
            if self._is_float(token):
                return True
        return False

    def _is_float(self, token: Token) -> bool:
        if token.tipo == TipoToken.NUMERO_REAL:
            return True
        if token.tipo == TipoToken.MEMORIA:
            reg = self.memoria.get(token.valor)
            return reg is not None and reg.startswith("D")
        return token.tipo == TipoToken.OPERADOR and token.valor in OPERACOES_DIVISIVAS

    def _define_token_headers(self, token: Token, eh_float: bool):
        header = ""
        reg_usado = None

        if token.tipo == TipoToken.MEMORIA:
            reg_usado = self.memoria.get(token.valor)
            if reg_usado is None:
                reg_usado = self.alocar_reg(eh_float=True)
                self.memoria[token.valor] = reg_usado
                label = self._criar_label_float(0.0)
                header += f"LDR R12, ={label}\n"
                header += f"VLDR {reg_usado}, [R12]\n"
            elif eh_float and not reg_usado.startswith("D"):
                reg_float = self.alocar_reg(eh_float=True)
                header += f"VMOV s0, {reg_usado}\n"
                header += f"VCVT.F64.S32 {reg_float}, s0\n"
                reg_usado = reg_float

        elif eh_float:
            if token.tipo == TipoToken.NUMERO_INTEIRO:
                token.valor = f"{float(token.valor):.2f}"
            reg_usado = self.alocar_reg(eh_float=True)
            label = self._criar_label_float(token.valor)
            header += f"LDR R12, ={label}\n"
            header += f"VLDR {reg_usado}, [R12]\n"

        elif token.tipo == TipoToken.NUMERO_INTEIRO:
            reg_usado = self.alocar_reg(eh_float=False)
            header += f"MOV {reg_usado}, #{token.valor}\n"

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

    def _criar_pow_loop(self, kw, reg_a, reg_b, reg_resultado, eh_float):
        before_op = []
        if eh_float:
            label_um = self._criar_label_float("1.00")
            before_op.append(f"LDR R12, ={label_um}")
            before_op.append(f"VLDR {reg_resultado}, [R12]")
        else:
            before_op.append(f"MOV {reg_resultado}, #1")

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

        before_op = []
        if operacao.valor == "^":
            before_op.extend(self._criar_pow_loop(kw, reg_a, reg_b, reg_resultado, eh_float))
            linha = ""
        else:
            linha = f"{kw} {reg_resultado}, {reg_a}, {reg_b}"

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

        if a.tipo != TipoToken.MEMORIA or a.valor.startswith("tmp_"):
            self.liberar_reg(reg_a)
        if b.tipo != TipoToken.MEMORIA or b.valor.startswith("tmp_"):
            self.liberar_reg(reg_b)

        tmp_key = f"tmp_{self.tmp_counter}"
        self.tmp_counter += 1
        self.memoria[tmp_key] = reg_resultado

        self.codigo_assembly.append(header)
        self.codigo_assembly.extend(before_op)
        if linha:
            self.codigo_assembly.append(linha)
        self.codigo_assembly.extend(after_op)

        return Token(TipoToken.MEMORIA, tmp_key, self.current_line, operacao.coluna)