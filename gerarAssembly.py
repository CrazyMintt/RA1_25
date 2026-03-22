from parseExpressao import Token, TipoToken

class geradorAssembly():
    def __init__(self):
        self.memoria = {}
        self.pilha = []
        self.codigo_assembly = []
        self.data_section = []
        self.current_line = 0
        self.data_counter = 0

    def gerarAssembly(self, tokens: list[Token]) -> str:
        for token in tokens:
            if token.linha != self.current_line:
                self.pilha = []
                self.current_line = token.linha

            if token.tipo == TipoToken.OPERADOR:
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.criar_op_line_assembly(a, b, token)
            elif token.tipo != TipoToken.PARENTESE_DIR and token.tipo != TipoToken.PARENTESE_ESQ:
                self.pilha.append(token)

        # monta o assembly final
        assembly = ".section .data\n"
        assembly += "\n".join(self.data_section)

        assembly += "\n\n.section .text\n.global _start\n_start:\n"
        assembly += "\n".join(self.codigo_assembly)

        return assembly

    def get_assembly_keyword(self, operacao: Token):
        if operacao.valor == "+":
            return "ADD"
        if operacao.valor == "-":
            return "SUB"
        if operacao.valor == "*":
            return "MUL"
        if operacao.valor == "/":
            return "VDIV.F32"

    def _criar_label_float(self, valor):
        label = f"num_{self.data_counter}"
        self.data_counter += 1
        self.data_section.append(f"{label}: .float {valor}")
        return label

    def _define_token_headers(self, token: Token, n_reg_usados: int):
        header = ""
        reg_usado = None

        if token.tipo == TipoToken.NUMERO_REAL:
            reg_usado = f"S{n_reg_usados}"
            label = self._criar_label_float(token.valor)

            header += f"""
            LDR R12, ={label}
            VLDR {reg_usado}, [R12]
            """

        elif token.tipo == TipoToken.NUMERO_INTEIRO:
            reg_usado = f"R{n_reg_usados}"
            header += f"MOV {reg_usado}, #{token.valor}\n"

        elif token.tipo == TipoToken.MEMORIA:
            reg_usado = self.memoria.get(token.valor, None)

            if not reg_usado:
                reg_usado = f"S{n_reg_usados}"
                label = self._criar_label_float(0.0)

                header += f"""
                LDR R12, ={label}
                VLDR {reg_usado}, [R12]
                """

        return header, reg_usado

    def create_op_headers(self, a, b, operacao):
        header = ""

        header_a, reg_a = self._define_token_headers(a, 0)
        header_b, reg_b = self._define_token_headers(b, 1)

        header += header_a + header_b

        return header, reg_a, reg_b

    def criar_op_line_assembly(self, a, b, operacao):
        kw = self.get_assembly_keyword(operacao)

        header, reg_a, reg_b = self.create_op_headers(a, b, operacao)

        linha = f"{kw} {reg_a}, {reg_a}, {reg_b}"

        self.codigo_assembly.append(header)
        self.codigo_assembly.append(linha)