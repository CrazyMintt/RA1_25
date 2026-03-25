from parseExpressao import Token, TipoToken

OPERACOES_DIVISIVAS = ["/", "//", "%"]


class geradorAssembly:
    def __init__(self):
        self.memoria = {}
        self.pilha = []
        self.codigo_assembly = []
        self.data_section = []  # precisa existir antes de usar append/extend

        # Tabela para seven-seg (HEX0)
        
        
        self.codigo_assembly.append("BL clear_display")
        self.data_section.append(".align 3")
        self.data_section.append("dez_float: .double 10.0")

        self.current_line = 0
        self.data_counter = 0
        self.tmp_counter = 0
        self.regs_livres_int = [f"R{i}" for i in reversed(range(0, 10))]
        self.regs_livres_float = [f"D{i}" for i in reversed(range(1, 32))]

    def gerar_data_section(self):
            mapa_7seg = {
                0: "0x3F", 1: "0x06", 2: "0x5B", 3: "0x4F",
                4: "0x66", 5: "0x6D", 6: "0x7D", 7: "0x07",
                8: "0x7F", 9: "0x6F"
            }
            self.data_section.append("tabela_7seg:")
            for num, hexa in mapa_7seg.items():
                self.data_section.append(f"    .byte {hexa}  @ dígito {num}")

    def gerar_biblioteca_standard(self):
        # Gerando a função display_int programaticamente
        self.codigo_assembly.append("\ndisplay_int:")
        
        # 1. Salva o contexto (Push)
        # Usamos todos os registros que o seu alocador gerencia
        regs_para_salvar = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "LR"]
        self.codigo_assembly.append(f"    PUSH {{{', '.join(regs_para_salvar)}}}")

        # 2. Chama a limpeza
        self.codigo_assembly.append("    BL clear_display")

        # 3. Aloca registros "locais" para a lógica da função
        reg_tabela = "R6"
        reg_hardware = "R7"
        reg_divisor = "R5"
        reg_valor = "R4"
        reg_contador = "R3"

        self.codigo_assembly.append(f"    LDR {reg_tabela}, =tabela_7seg")
        self.codigo_assembly.append(f"    LDR {reg_hardware}, =0xFF200020")
        self.codigo_assembly.append(f"    MOV {reg_divisor}, #10")
        self.codigo_assembly.append(f"    MOV {reg_valor}, R0")

        # 4. Lógica de loop (usando labels dinâmicas se quiser)
        self.codigo_assembly.append("    CMP R4, #0")
        self.codigo_assembly.append("    BNE display_int_loop")
        
        # Caso seja Zero
        self.codigo_assembly.append("    MOV R1, #0")
        self.codigo_assembly.append(f"    LDRB R2, [{reg_tabela}, R1]")
        self.codigo_assembly.append(f"    STRB R2, [{reg_hardware}]")
        self.codigo_assembly.append("    B fim_display_int")

        self.codigo_assembly.append("\ndisplay_int_loop:")
        self.codigo_assembly.append(f"    MOV {reg_contador}, #0")

        self.codigo_assembly.append("\nloop_body:")
        self.codigo_assembly.append(f"    CMP {reg_contador}, #6")
        self.codigo_assembly.append("    BEQ fim_display_int")

        self.codigo_assembly.append(f"    MOV R1, {reg_valor}")
        self.codigo_assembly.append("    BL div_mod")
        
        self.codigo_assembly.append(f"    LDRB R2, [{reg_tabela}, R1]")
        self.codigo_assembly.append(f"    STRB R2, [{reg_hardware}]")
        
        self.codigo_assembly.append(f"    MOV {reg_valor}, R0")
        self.codigo_assembly.append(f"    CMP {reg_valor}, #0")
        self.codigo_assembly.append("    BEQ fim_display_int")

        # Lógica de pulo de endereço (HEX3 -> HEX4)
        self.codigo_assembly.append(f"    ADD {reg_hardware}, {reg_hardware}, #1")
        self.codigo_assembly.append(f"    LDR R8, =0xFF200024")
        self.codigo_assembly.append(f"    CMP {reg_hardware}, R8")
        self.codigo_assembly.append("    BNE skip_jump")
        self.codigo_assembly.append(f"    LDR {reg_hardware}, =0xFF200030")
        
        self.codigo_assembly.append("\nskip_jump:")
        self.codigo_assembly.append(f"    ADD {reg_contador}, {reg_contador}, #1")
        self.codigo_assembly.append("    B loop_body")

        self.codigo_assembly.append("\nfim_display_int:")
        self.codigo_assembly.append(f"    POP {{{', '.join(regs_para_salvar)}}}")
        self.codigo_assembly.append("    BX LR")

    def gerar_clear_display(self):
        self.codigo_assembly.append("\nclear_display:")
        self.codigo_assembly.append("    PUSH {R1, R2, LR}")
        self.codigo_assembly.append("    MOV R2, #0")
        
        # Limpa HEX0 a HEX3
        self.codigo_assembly.append("    LDR R1, =0xFF200020")
        self.codigo_assembly.append("    STR R2, [R1]")
        
        # Limpa HEX4 a HEX5
        self.codigo_assembly.append("    LDR R1, =0xFF200030")
        self.codigo_assembly.append("    STRH R2, [R1]")
        
        self.codigo_assembly.append("    POP {R1, R2, LR}")
        self.codigo_assembly.append("    BX LR")

    def gerar_div_mod(self):
        self.codigo_assembly.append("\ndiv_mod:")
        self.codigo_assembly.append("    MOV R0, #0")
        
        self.codigo_assembly.append("\ndiv_loop:")
        self.codigo_assembly.append("    CMP R1, R5")
        self.codigo_assembly.append("    BLT div_end")
        self.codigo_assembly.append("    SUB R1, R1, R5")
        self.codigo_assembly.append("    ADD R0, R0, #1")
        self.codigo_assembly.append("    B div_loop")
        
        self.codigo_assembly.append("\ndiv_end:")
        self.codigo_assembly.append("    BX LR")

    def gerar_display_float(self):
        self.codigo_assembly.append("\ndisplay_float:")
        
        regs_salvar = ["R1", "R2", "R3", "R4", "LR"]
        self.codigo_assembly.append(f"    PUSH {{{', '.join(regs_salvar)}}}")
        self.codigo_assembly.append("    BL clear_display")

        # Converte o número total para inteiro (Parte Inteira)
        self.codigo_assembly.append("    VCVT.S32.F64 S0, D0")
        self.codigo_assembly.append("    VMOV R0, S0")
        self.codigo_assembly.append("    MOV R3, R0")

        # Isola a parte decimal
        self.codigo_assembly.append("    VCVT.F64.S32 D1, S0")
        self.codigo_assembly.append("    VSUB.F64 D2, D0, D1")

        # Multiplica por 10.0
        self.codigo_assembly.append("    LDR R1, =dez_float")
        self.codigo_assembly.append("    VLDR D3, [R1]")
        self.codigo_assembly.append("    VMUL.F64 D2, D2, D3")

        # Converte o decimal para inteiro
        self.codigo_assembly.append("    VCVT.S32.F64 S1, D2")
        self.codigo_assembly.append("    VMOV R4, S1")

        self.codigo_assembly.append("    LDR R1, =tabela_7seg")

        # Escreve a Casa decimal no HEX0
        self.codigo_assembly.append("    LDRB R2, [R1, R4]")
        self.codigo_assembly.append("    LDR R0, =0xFF200020")
        self.codigo_assembly.append("    STRB R2, [R0]")

        # Escreve a Parte inteira no HEX1 
        self.codigo_assembly.append("    LDRB R2, [R1, R3]")
        self.codigo_assembly.append("    LDR R0, =0xFF200021")
        self.codigo_assembly.append("    STRB R2, [R0]")

        self.codigo_assembly.append(f"    POP {{{', '.join(regs_salvar)}}}")
        self.codigo_assembly.append("    BX LR")

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

        self.codigo_assembly.append("\nfim_programa:")
        self.codigo_assembly.append("    B fim_programa")
        self.gerar_data_section()  #Preenche self.data_section
        self.gerar_biblioteca_standard() # Isso preenche self.codigo_assembly
        self.gerar_clear_display()
        self.gerar_div_mod()
        self.gerar_display_float()

        # No final, apenas junta tudo
        assembly = ".section .data\n" + "\n".join(self.data_section)
        assembly += "\n\n.section .text\n" + "\n".join(self.codigo_assembly)
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
            valor = int(token.valor)

            reg_usado = self.alocar_reg(eh_float=False)

            # se número for grande
            if abs(valor) > 255:
                label = f"int_{self.data_counter}"
                self.data_counter += 1
                self.data_section.append(f"{label}: .word {valor}")

                header += f"LDR R12, ={label}\n"
                header += f"LDR {reg_usado}, [R12]\n"
            else:
                header += f"MOV {reg_usado}, #{valor}\n"

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
        linhas.append(f"BGE display_abs_ok_{op_id}"
        )
        linhas.append("RSB R0, R0, #0")
        linhas.append(f"display_abs_ok_{op_id}:")

        # Mostra apenas o último dígito (0..9)
        linhas.append("BL display_int")
       

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

print("\n==== TESTE DIVISÃO ====\n")
tokens_div = [
    Token(TipoToken.NUMERO_INTEIRO, "10", 1, 1),
    Token(TipoToken.NUMERO_INTEIRO, "2", 1, 3),
    Token(TipoToken.OPERADOR, "/", 1, 5),
]
gerador = geradorAssembly()
print(gerador.gerarAssembly(tokens_div))

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

print("\n==== TESTE NUMERO GRANDE ====\n")
tokens_grande = [
    Token(TipoToken.NUMERO_INTEIRO, "1012", 1, 1),
    Token(TipoToken.NUMERO_INTEIRO, "9023", 1, 11),
    Token(TipoToken.OPERADOR, "+", 1, 21),
]
gerador = geradorAssembly()
print(gerador.gerarAssembly(tokens_grande))


print("==== TESTE MÚLTIPLAS LINHAS ====\n")


tokens_multi = [

    Token(TipoToken.NUMERO_INTEIRO, "10", 1, 1),
    Token(TipoToken.NUMERO_INTEIRO, "20", 1, 4),
    Token(TipoToken.OPERADOR, "+", 1, 7),
    

    Token(TipoToken.NUMERO_REAL, "5.5", 2, 1),
    Token(TipoToken.NUMERO_INTEIRO, "20", 2, 5),
    Token(TipoToken.OPERADOR, "/", 2, 7),
    

    Token(TipoToken.NUMERO_INTEIRO, "2", 3, 1),
    Token(TipoToken.NUMERO_INTEIRO, "4", 3, 3),
    Token(TipoToken.OPERADOR, "^", 3, 5),
]

gerador = geradorAssembly()
assembly_final = gerador.gerarAssembly(tokens_multi)
print(assembly_final)