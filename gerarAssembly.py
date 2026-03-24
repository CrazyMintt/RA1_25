from parseExpressao import Token, TipoToken

OPERACOES_DIVISIVAS = ["/", "//", "%"]


class geradorAssembly:
    def __init__(self):
        self.memoria = {}
        self.pilha = []
        self.codigo_assembly = []
        self.data_section = []  # precisa existir antes de usar append/extend

        # Tabela para seven-seg (HEX0)
        self.data_section.append("tabela_7seg:")
        self.data_section.extend([
            ".byte 0x3F",  # 0
            ".byte 0x06",  # 1
            ".byte 0x5B",  # 2
            ".byte 0x4F",  # 3
            ".byte 0x66",  # 4
            ".byte 0x6D",  # 5
            ".byte 0x7D",  # 6
            ".byte 0x07",  # 7
            ".byte 0x7F",  # 8
            ".byte 0x6F",  # 9
        ])
        self.codigo_assembly.append("BL clear_display")
        self.data_section.append(".align 3")
        self.data_section.append("dez_float: .double 10.0")

        self.current_line = 0
        self.data_counter = 0
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

    def gerarAssembly(self, tokens: list[Token]) -> str:
        for token in tokens:
        

            if token.linha != self.current_line:
                self.pilha = []
                self.current_line = token.linha

            if token.tipo == TipoToken.OPERADOR:
                b = self.pilha.pop()
                a = self.pilha.pop()
                new_token = self.criar_op_line_assembly(a, b, token)
                self.pilha.append(new_token)

            elif token.tipo not in (TipoToken.PARENTESE_DIR, TipoToken.PARENTESE_ESQ):
                self.pilha.append(token)

        assembly = ".section .data\n"
        assembly += "\n".join(self.data_section)
        assembly += "\n\n.section .text\n.global _start\n_start:\n"
        assembly += "\n".join(self.codigo_assembly)
        assembly += "\n\nfim:\nB fim\n"

        assembly += """
display:
    PUSH {R1, R2, LR}

    LDR R1, =tabela_7seg
    LDRB R2, [R1, R0]

    LDR R1, =0xFF200020
    STR R2, [R1]

    POP {R1, R2, LR}
    BX LR

display_float:
    PUSH {R1, R2, R3, R4, LR}

    VCVT.S32.F64 S0, D0
    VMOV R0, S0
    MOV R3, R0

    VCVT.F64.S32 D1, S0
    VSUB.F64 D2, D0, D1

    LDR R1, =dez_float
    VLDR D3, [R1]
    VMUL.F64 D2, D2, D3

    VCVT.S32.F64 S1, D2
    VMOV R4, S1

    LDR R1, =tabela_7seg

    LDRB R2, [R1, R4]
    LDR R0, =0xFF200020
    STR R2, [R0]

    LDRB R2, [R1, R3]
    LDR R0, =0xFF200030
    STR R2, [R0]

    POP {R1, R2, R3, R4, LR}
    BX LR

clear_display:
    PUSH {R1, R2, LR}

    MOV R2, #0

    LDR R1, =0xFF200020
    STR R2, [R1]

    LDR R1, =0xFF200030
    STR R2, [R1]

    LDR R1, =0xFF200040
    STR R2, [R1]

    LDR R1, =0xFF200050
    STR R2, [R1]

    LDR R1, =0xFF200060
    STR R2, [R1]

    LDR R1, =0xFF200070
    STR R2, [R1]

    POP {R1, R2, LR}
    BX LR
"""
        return assembly

    def get_assembly_keyword(self, operacao: Token, eh_float: bool) -> str:
        if eh_float:
            mapa = {
                "+": "VADD.F64",
                "-": "VSUB.F64",
                "*": "VMUL.F64",
                "/": "VDIV.F64",
                "//": "VDIV.F64",
                "%": "VDIV.F64",
                "^": "VMUL.F64",
            }
        else:
            mapa = {
                "+": "ADD",
                "-": "SUB",
                "*": "MUL",
                "^": "MUL",
            }

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

    def _op_creates_floats(self, operacao: Token) -> bool:
        return operacao.valor in OPERACOES_DIVISIVAS

    def create_op_headers(self, a: Token, b: Token, operacao: Token):
        eh_float = self._is_float(a) or self._is_float(b) or self._op_creates_floats(operacao)
        header_a, reg_a = self._define_token_headers(a, eh_float)
        header_b, reg_b = self._define_token_headers(b, eh_float)
        return header_a + header_b, reg_a, reg_b, eh_float

    def convert_64b_to_int(self, reg):
        linhas = []
        linhas.append(f"VCVT.S32.F64 S0, {reg}")
        self.liberar_reg(reg)
        reg_saida = self.alocar_reg(eh_float=False)
        linhas.append(f"VMOV {reg_saida}, S0")
        return linhas, reg_saida

    def _criar_pow_loop(self, kw, reg_a, reg_b, reg_resultado, eh_float):
        before_op = []
        if eh_float:
            label_um = self._criar_label_float("1.00")
            before_op.append(f"LDR R12, ={label_um}")
            before_op.append(f"VLDR {reg_resultado}, [R12]")
        else:
            before_op.append(f"MOV {reg_resultado}, #1")

        loop_id = self.tmp_counter
        lbl_loop = f"pow_loop_{loop_id}"
        lbl_end = f"pow_end_{loop_id}"

        before_op.append(f"{lbl_loop}:")
        before_op.append(f"CMP {reg_b}, #0")
        before_op.append(f"BEQ {lbl_end}")
        before_op.append(f"{kw} {reg_resultado}, {reg_resultado}, {reg_a}")
        before_op.append(f"SUB {reg_b}, {reg_b}, #1")
        before_op.append(f"B {lbl_loop}")
        before_op.append(f"{lbl_end}:")

        return before_op

    def _emitir_display_resultado(self, reg_resultado: str, eh_float: bool, op_id: int):
        linhas = []

        if eh_float:
            linhas.append(f"VMOV.F64 D0, {reg_resultado}")
            linhas.append("BL display_float")
            return linhas
        else:
            linhas.append(f"MOV R0, {reg_resultado}")

        # Se for negativo, mostra o valor absoluto no display
        linhas.append("CMP R0, #0")
        linhas.append(f"BGE display_abs_ok_{op_id}")
        linhas.append("RSB R0, R0, #0")
        linhas.append(f"display_abs_ok_{op_id}:")

        # Mostra apenas o último dígito (0..9)
        linhas.append("MOV R1, #10")
        linhas.append(f"display_mod_loop_{op_id}:")
        linhas.append("CMP R0, R1")
        linhas.append(f"BLT display_mod_done_{op_id}")
        linhas.append("SUB R0, R0, R1")
        linhas.append(f"B display_mod_loop_{op_id}")
        linhas.append(f"display_mod_done_{op_id}:")
        linhas.append("BL display")

        return linhas

    def criar_op_line_assembly(self, a: Token, b: Token, operacao: Token) -> Token:
        op_id = self.tmp_counter

        header, reg_a, reg_b, eh_float = self.create_op_headers(a, b, operacao)
        kw = self.get_assembly_keyword(operacao, eh_float)

        reg_resultado = self.alocar_reg(eh_float=eh_float)

        before_op = []
        if operacao.valor == "^":
            before_op.extend(self._criar_pow_loop(kw, reg_a, reg_b, reg_resultado, eh_float))
            linha = ""
        else:
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

        self.liberar_reg(reg_a)
        self.liberar_reg(reg_b)

        tmp_key = f"tmp_{self.tmp_counter}"
        self.tmp_counter += 1
        self.memoria[tmp_key] = reg_resultado

        self.codigo_assembly.append(header)
        self.codigo_assembly.extend(before_op)
        if linha:
            self.codigo_assembly.append(linha)
        self.codigo_assembly.extend(after_op)
        self.codigo_assembly.extend(self._emitir_display_resultado(reg_resultado, eh_float, op_id))

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
    Token(TipoToken.NUMERO_INTEIRO, "3", 1, 5),
    Token(TipoToken.OPERADOR, "%", 1, 9),
]
gerador = geradorAssembly()
print(gerador.gerarAssembly(tokens_mod))

print("\n==== TESTE FLOAT ====\n")
tokens_float = [
    Token(TipoToken.NUMERO_REAL, "10.0", 1, 1),
    Token(TipoToken.NUMERO_REAL, "3.0", 1, 5),
    Token(TipoToken.OPERADOR, "/", 1, 9),
]
gerador = geradorAssembly()
print(gerador.gerarAssembly(tokens_float))