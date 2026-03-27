'''
Equipe:
Bruno Betiatto Alves @Brunobetiatto
Bruno Himovski Opuszka Machado Dutra @CrazyMintt
Leonardo Saito @Leosaito632
Vitor Nicoletti @vitorNicoletti

GRUPO: RA1-25
'''
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
        self.label_display_counter = 0

    def alocar_reg(self, eh_float: bool) -> str:
        pool = self.regs_livres_float if eh_float else self.regs_livres_int
        if not pool:
            raise RuntimeError("Registradores esgotados")
        return pool.pop()

    def liberar_reg(self, reg: str):
        # FIX 1: removidos os print de debug que poluíam a saída
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

                # FIX 2: variável crua saindo de parênteses seria confundida com
                # destino de atribuição pelo loop principal. Promove para tmp_
                # para que seja tratada como valor, não como alvo de escrita.
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
        """
        Salva o valor de token_origem em reg_destino (sempre D, 64 bits).
        Faz conversão int -> double quando necessário.
        """
        if token_origem.tipo == TipoToken.NUMERO_INTEIRO:
            label = self._criar_label_float(f"{float(token_origem.valor):.2f}")
            self.codigo_assembly.append(f"    LDR R12, ={label}")
            self.codigo_assembly.append(f"    VLDR {reg_destino}, [R12]")

        elif token_origem.tipo == TipoToken.NUMERO_REAL:
            label = self._criar_label_float(token_origem.valor)
            self.codigo_assembly.append(f"    LDR R12, ={label}")
            self.codigo_assembly.append(f"    VLDR {reg_destino}, [R12]")

        elif token_origem.tipo == TipoToken.MEMORIA:
            reg_origem = self.memoria.get(token_origem.valor)

            if reg_origem is None:
                # variável ainda não inicializada -> zero
                label = self._criar_label_float("0.0")
                self.codigo_assembly.append(f"    LDR R12, ={label}")
                self.codigo_assembly.append(f"    VLDR {reg_destino}, [R12]")

            elif reg_origem.startswith("D"):
                # D -> D: cópia direta
                self.codigo_assembly.append(f"    VMOV.F64 {reg_destino}, {reg_origem}")

            else:
                # FIX 3: R (inteiro) -> D (double): converte via s0
                self.codigo_assembly.append(f"    VMOV  s0, {reg_origem}")
                self.codigo_assembly.append(f"    VCVT.F64.S32 {reg_destino}, s0")

        else:
            raise ValueError(f"Tipo inesperado em _salvar_valor_a_reg: {token_origem.tipo}")

    def _gerar_linha_assembly(self, tokens_line):
        pilha = []
        for token in tokens_line:
            if token.tipo == TipoToken.MEMORIA and not token.valor.startswith("tmp_"):
                # FIX 4: não aloca registrador antes de saber se é atribuição ou leitura.
                # Antes, sempre alocava um D mesmo quando o token era só leitura,
                # desperdiçando registradores.
                try:
                    token_atribuir = pilha.pop()
                    # só agora sabemos que é atribuição — pega ou aloca o registrador
                    reg_var = self.memoria.get(token.valor)
                    # garante que sempre será D, já que _salvar_valor_a_reg usa VFP
                    if not reg_var or not reg_var.startswith("D"):
                        reg_var = self.alocar_reg(True)

                    self._salvar_valor_a_reg(token_atribuir, reg_var)
                    self.memoria[token.valor] = reg_var
                    
                    # Reapendado para compatibilidade com o loop de display final
                    pilha.append(token_atribuir)
                except IndexError:
                    # FIX 5: captura apenas IndexError (pilha vazia = é leitura)
                    # O bare "except" anterior engolia qualquer erro, tornando
                    # bugs silenciosos e impossíveis de depurar.
                    pilha.append(token)
            elif token.tipo == TipoToken.KEYWORD:
                if token.valor == "RES":
                    n_tk = pilha.pop()
                    linha_res = self.current_line - int(n_tk.valor)
                    reg_res = self.memoria.get(f"res_linha_{linha_res}")
                    coluna = token.coluna if hasattr(token, 'coluna') else 0
                    pilha.append(Token(TipoToken.MEMORIA, f"res_linha_{linha_res}", self.current_line, coluna))
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
            valor_anterior = None
            for token in tokens_line:
                if valor_anterior == None:
                    valor_anterior = token
                if token.tipo == TipoToken.KEYWORD and token.valor == "RES":
                    linha_para_salvar = i - int(valor_anterior.valor)
                    if not self.memoria.get(f"res_linha_{linha_para_salvar}", None):
                        eh_float = self.line_is_float(token_matrix[linha_para_salvar])
                        reg_res = self.alocar_reg(eh_float)
                        nome_variavel = f"res_linha_{linha_para_salvar}"
                        self.memoria[nome_variavel] = reg_res
                        token_matrix[linha_para_salvar].append(
                            Token(TipoToken.MEMORIA, nome_variavel, linha_para_salvar, 0)
                        )
        return token_matrix

    def gerarAssembly(self, token_matrix: list[list[Token]]) -> tuple[str, list]:
        self.codigo_assembly = []
        self.data_section = [] 
        self.label_display_counter = 0 

        self.gerar_data_section()

        token_matrix = self.resolver_RES(token_matrix)
        
        for i, tokens_line in enumerate(token_matrix):
            self.current_line = i
            tokens_line = self.resolver_parenteses(tokens_line)
            pilha_final = self._gerar_linha_assembly(tokens_line)
            
            while pilha_final: 
                token_res = pilha_final.pop()
                reg_res = self.memoria.get(token_res.valor)
                
                if reg_res:
                    eh_float = "D" in reg_res
                    self.codigo_assembly.extend(self._emitir_display_resultado(reg_res, eh_float))
                    
                    if token_res.valor.startswith("tmp_"):
                        self.liberar_reg(reg_res)
                        del self.memoria[token_res.valor]
        return self._formatar_output_final(), []

    def _formatar_output_final(self) -> str:
        self.codigo_assembly.append("\nfim:")
        self.codigo_assembly.append("    B fim\n")
        
        self.gerar_biblioteca_standard()
        self.gerar_clear_display()
        self.gerar_div_mod()
        self.gerar_display_float()
        
        assembly  = ".section .data\n"
        assembly += "\n".join(list(dict.fromkeys(self.data_section)))
        
        assembly += "\n\n.section .text\n.align 2\n.global _start\n_start:\n"
        assembly += "\n".join(self.codigo_assembly)
        
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
                header += f"    LDR R12, ={label}\n"
                header += f"    VLDR {reg_usado}, [R12]\n"
            elif eh_float and not reg_usado.startswith("D"):
                reg_float = self.alocar_reg(eh_float=True)
                header += f"    VMOV s0, {reg_usado}\n"
                header += f"    VCVT.F64.S32 {reg_float}, s0\n"
                reg_usado = reg_float

        elif eh_float:
            if token.tipo == TipoToken.NUMERO_INTEIRO:
                token.valor = f"{float(token.valor):.2f}"
            reg_usado = self.alocar_reg(eh_float=True)
            label = self._criar_label_float(token.valor)
            header += f"    LDR R12, ={label}\n"
            header += f"    VLDR {reg_usado}, [R12]\n"

        elif token.tipo == TipoToken.NUMERO_INTEIRO:
            reg_usado = self.alocar_reg(eh_float=False)
            header += f"    MOV {reg_usado}, #{token.valor}\n"

        return header, reg_usado

    def _op_creates_floats(self, operacao) -> bool:
        return operacao.valor in OPERACOES_DIVISIVAS

    def create_op_headers(self, a: Token, b: Token, operacao: Token):
        eh_float = self._is_float(a) or self._is_float(b) or self._op_creates_floats(operacao)
        header_a, reg_a = self._define_token_headers(a, eh_float)
        header_b, reg_b = self._define_token_headers(b, eh_float)

        if eh_float:
            if not reg_a.startswith("D"):
                reg_f = self.alocar_reg(True)
                header_a += f"    VMOV s0, {reg_a}\n    VCVT.F64.S32 {reg_f}, s0\n"
                self.liberar_reg(reg_a)
                reg_a = reg_f
            if not reg_b.startswith("D"):
                reg_f = self.alocar_reg(True)
                header_b += f"    VMOV s0, {reg_b}\n    VCVT.F64.S32 {reg_f}, s0\n"
                self.liberar_reg(reg_b)
                reg_b = reg_f
                
        return header_a + header_b, reg_a, reg_b, eh_float

    def convert_64b_to_int(self, reg):
        linhas = []
        linhas.append(f"    vcvt.s32.f64 s0, {reg}")
        self.liberar_reg(reg)
        reg_saida = self.alocar_reg(eh_float=False)
        linhas.append(f"    vmov {reg_saida}, s0")
        return linhas, reg_saida

    def _criar_pow_loop(self, kw, reg_a, reg_b, reg_resultado, eh_float):
        before_op = []
        reg_contador = reg_b
        
        if reg_b.startswith("D"):
            reg_tmp_int = self.alocar_reg(eh_float=False)
            before_op.append(f"    VCVT.S32.F64 s0, {reg_b}")
            before_op.append(f"    VMOV {reg_tmp_int}, s0")
            reg_contador = reg_tmp_int

        if eh_float:
            label_um = self._criar_label_float("1.00")
            before_op.append(f"    LDR R12, ={label_um}")
            before_op.append(f"    VLDR {reg_resultado}, [R12]")
        else:
            before_op.append(f"    MOV {reg_resultado}, #1")

        loop_id = self.tmp_counter
        lbl_loop = f"pow_loop_{loop_id}"
        lbl_end = f"pow_end_{loop_id}"
        
        before_op.append(f"{lbl_loop}:")
        before_op.append(f"    CMP {reg_contador}, #0") 
        before_op.append(f"    BEQ {lbl_end}")
        before_op.append(f"    {kw} {reg_resultado}, {reg_resultado}, {reg_a}")
        before_op.append(f"    SUB {reg_contador}, {reg_contador}, #1") 
        before_op.append(f"    B {lbl_loop}")
        before_op.append(f"{lbl_end}:")

        if reg_contador != reg_b:
            self.liberar_reg(reg_contador)

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
            linha = f"    {kw} {reg_resultado}, {reg_a}, {reg_b}"

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
            after_op.append(f"    MUL {reg_saida}, {reg_resultado}, {reg_b}")
            after_op.append(f"    SUB {reg_saida}, {reg_a}, {reg_saida}")
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

        coluna = operacao.coluna if hasattr(operacao, 'coluna') else 0
        return Token(TipoToken.MEMORIA, tmp_key, self.current_line, coluna)

# =========================================================================
# Biblioteca (Funções de Display e Base de Dados)
# =========================================================================

    def gerar_data_section(self):
        mapa_7seg = {
            0: "0x3F", 1: "0x06", 2: "0x5B", 3: "0x4F",
            4: "0x66", 5: "0x6D", 6: "0x7D", 7: "0x07",
            8: "0x7F", 9: "0x6F"
        }
        self.data_section.append(".align 2") 
        self.data_section.append("tabela_7seg:")
        for num, hexa in mapa_7seg.items():
            self.data_section.append(f"    .byte {hexa}  @ dígito {num}")
            
        self.data_section.append(".align 3") 
        self.data_section.append("dez_float: .double 10.00")

    def _criar_label_float(self, valor) -> str:
        label = f"num_{self.data_counter}"
        self.data_counter += 1
        self.data_section.append(".align 3") 
        self.data_section.append(f"{label}: .double {valor}")
        return label

    def gerar_biblioteca_standard(self):
        self.codigo_assembly.append("\ndisplay_int:")
        regs_para_salvar = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "LR"]
        self.codigo_assembly.append(f"    PUSH {{{', '.join(regs_para_salvar)}}}")
        self.codigo_assembly.append("    BL clear_display")

        reg_tabela = "R6"
        reg_hardware = "R7"
        reg_divisor = "R5"
        reg_valor = "R4"
        reg_contador = "R3"

        self.codigo_assembly.append(f"    LDR {reg_tabela}, =tabela_7seg")
        self.codigo_assembly.append(f"    LDR {reg_hardware}, =0xFF200020")
        self.codigo_assembly.append(f"    MOV {reg_divisor}, #10")
        self.codigo_assembly.append(f"    MOV {reg_valor}, R0")

        self.codigo_assembly.append("    CMP R4, #0")
        self.codigo_assembly.append("    BNE display_int_loop")
        
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

        self.codigo_assembly.append(f"    ADD {reg_hardware}, {reg_hardware}, #1")
        self.codigo_assembly.append(f"    LDR R8, =0xFF200024")
        self.codigo_assembly.append(f"    CMP {reg_hardware}, R8")
        self.codigo_assembly.append("    BNE skip_jump")
        self.codigo_assembly.append(f"    LDR {reg_hardware}, =0xFF200030")
        
        self.codigo_assembly.append("\nskip_jump:")
        self.codigo_assembly.append(f"    ADD {reg_contador}, {reg_contador}, #1")
        self.codigo_assembly.append("    B loop_body")

        self.codigo_assembly.append("\nfim_display_int:")
        self.codigo_assembly.append("    BKPT  @ Pausa apos exibir resultado inteiro")
        self.codigo_assembly.append(f"    POP {{{', '.join(regs_para_salvar)}}}")
        self.codigo_assembly.append("    BX LR")

    def gerar_clear_display(self):
        self.codigo_assembly.append("\nclear_display:")
        self.codigo_assembly.append("    PUSH {R1, R2, LR}")
        self.codigo_assembly.append("    MOV R2, #0")
        
        self.codigo_assembly.append("    LDR R1, =0xFF200020")
        self.codigo_assembly.append("    STR R2, [R1]")
        
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
        
        regs_salvar = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "LR"]
        self.codigo_assembly.append(f"    PUSH {{{', '.join(regs_salvar)}}}")
        self.codigo_assembly.append("    BL clear_display")

        self.codigo_assembly.append("    VCVT.S32.F64 S0, D0")
        self.codigo_assembly.append("    VMOV R4, S0")
        self.codigo_assembly.append("    VCVT.F64.S32 D1, S0")
        self.codigo_assembly.append("    VSUB.F64 D2, D0, D1")
        self.codigo_assembly.append("    LDR R1, =dez_float")
        self.codigo_assembly.append("    VLDR D3, [R1]")
        self.codigo_assembly.append("    VMUL.F64 D2, D2, D3")
        self.codigo_assembly.append("    VCVT.S32.F64 S1, D2")
        self.codigo_assembly.append("    VMOV R8, S1")

        self.codigo_assembly.append("    LDR R6, =tabela_7seg")
        self.codigo_assembly.append("    LDR R7, =0xFF200020")
        self.codigo_assembly.append("    MOV R9, #0")
        self.codigo_assembly.append("    MOV R5, #10")
        
        self.codigo_assembly.append("    LDRB R2, [R6, R8]")
        self.codigo_assembly.append("    LDR R10, [R7]")
        self.codigo_assembly.append("    MOV R3, #0xFF")
        self.codigo_assembly.append("    LSL R3, R3, R9")
        self.codigo_assembly.append("    BIC R10, R10, R3")
        self.codigo_assembly.append("    LSL R2, R2, R9")
        self.codigo_assembly.append("    ORR R10, R10, R2")
        self.codigo_assembly.append("    STR R10, [R7]")
        
        self.codigo_assembly.append("    ADD R9, R9, #16") 

        self.codigo_assembly.append("\ndisplay_float_loop:")
        self.codigo_assembly.append("    MOV R1, R4")
        self.codigo_assembly.append("    BL div_mod")
        self.codigo_assembly.append("    LDRB R2, [R6, R1]")

        self.codigo_assembly.append("    LDR R10, [R7]")
        self.codigo_assembly.append("    MOV R3, #0xFF")
        self.codigo_assembly.append("    LSL R3, R3, R9")
        self.codigo_assembly.append("    BIC R10, R10, R3")
        self.codigo_assembly.append("    LSL R2, R2, R9")
        self.codigo_assembly.append("    ORR R10, R10, R2")
        self.codigo_assembly.append("    STR R10, [R7]")

        self.codigo_assembly.append("    MOV R4, R0")
        self.codigo_assembly.append("    CMP R4, #0")
        self.codigo_assembly.append("    BEQ fim_display_float")

        self.codigo_assembly.append("    ADD R9, R9, #8")
        self.codigo_assembly.append("    CMP R9, #32")
        self.codigo_assembly.append("    BNE display_float_loop")
        
        self.codigo_assembly.append("    LDR R7, =0xFF200030")
        self.codigo_assembly.append("    MOV R9, #0")
        self.codigo_assembly.append("    B display_float_loop")

        self.codigo_assembly.append("\nfim_display_float:")
        self.codigo_assembly.append("    BKPT  @ Pausa apos exibir resultado float")
        self.codigo_assembly.append(f"    POP {{{', '.join(regs_salvar)}}}")
        self.codigo_assembly.append("    BX LR")

    def _emitir_display_resultado(self, reg_resultado: str, eh_float: bool):
        linhas = []
        lbl_id = self.label_display_counter
        self.label_display_counter += 1

        if eh_float:
            linhas.append(f"    VMOV.F64 D0, {reg_resultado}")
            linhas.append("    BL display_float")
        else:
            linhas.append(f"    MOV R0, {reg_resultado}")
            linhas.append("    CMP R0, #0")
            linhas.append(f"    BGE display_abs_ok_{lbl_id}")
            linhas.append("    RSB R0, R0, #0")
            linhas.append(f"display_abs_ok_{lbl_id}:")
            linhas.append("    BL display_int")
        return linhas