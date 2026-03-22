from parseExpressao import Token, TipoToken


class geradorAssembly():
    def __init__(self):
        self.memoria = {}
        self.pilha = []
        self.codigo_assembly = []
        self.data_section = []
        self.current_line = 0
        self.data_counter = 0
        self.tmp_counter = 0
        self.regs_livres_int = [f"R{i}" for i in reversed(range(0, 10))]
        print(self.regs_livres_int)

        self.regs_livres_float = [f"S{i}" for i in reversed(range(0, 16))]
        print(self.regs_livres_float)


    def alocar_reg(self, eh_float: bool) -> str:
        pool = self.regs_livres_float if eh_float else self.regs_livres_int
        if not pool:
            raise RuntimeError("Registradores esgotados")
        n = pool.pop()
        return n

    def liberar_reg(self, reg: str):
        print(f"tentando liberar reg: {reg}")
        
        
        if reg.startswith("S"):
            print(self.regs_livres_float)
            self.regs_livres_float.append(reg)
        else:
            print(self.regs_livres_int)
            self.regs_livres_int.append(reg)

    def gerarAssembly(self, tokens: list[Token]) -> str:
        for token in tokens:
            print(f"pilha: {self.pilha}")

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

        assembly  = ".section .data\n"
        assembly += "\n".join(self.data_section)
        assembly += "\n\n.section .text\n.global _start\n_start:\n"
        assembly += "\n".join(self.codigo_assembly)
        return assembly

    def get_assembly_keyword(self, operacao: Token, eh_float: bool) -> str:
        if eh_float:
            mapa = {"+": "VADD.F32", "-": "VSUB.F32",
                    "*": "VMUL.F32", "/": "VDIV.F32"}
        else:
            mapa = {"+": "ADD", "-": "SUB",
                    "*": "MUL", "/": "SDIV"}

        kw = mapa.get(operacao.valor)
        if kw is None:
            raise ValueError(f"Operador desconhecido: '{operacao.valor}'")
        return kw

    def _criar_label_float(self, valor) -> str:
        label = f"num_{self.data_counter}"
        self.data_counter += 1
        self.data_section.append(f"{label}: .float {valor}")
        return label

    def _is_float(self, token: Token) -> bool:
        """Diz se um token representa um valor float."""
        if token.tipo == TipoToken.NUMERO_REAL:
            return True
        if token.tipo == TipoToken.MEMORIA:
            reg = self.memoria.get(token.valor)
            return reg is not None and reg.startswith("S")
        return False

    def _define_token_headers(self, token: Token, eh_float: bool):
        """
        Gera o header de carregamento e retorna (header, reg_alocado).
        Para MEMORIA, apenas lê o registrador já existente — sem alocar novo.
        """
        header = ""
        reg_usado = None

        if token.tipo == TipoToken.NUMERO_REAL:
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

    def create_op_headers(self, a: Token, b: Token, operacao: Token):
        eh_float = self._is_float(a) or self._is_float(b)

        header_a, reg_a = self._define_token_headers(a, eh_float)
        header_b, reg_b = self._define_token_headers(b, eh_float)

        return header_a + header_b, reg_a, reg_b, eh_float

    def criar_op_line_assembly(self, a: Token, b: Token, operacao: Token) -> Token:
        header, reg_a, reg_b, eh_float = self.create_op_headers(a, b, operacao)
        kw = self.get_assembly_keyword(operacao, eh_float)

        # aloca registrador exclusivo para o resultado antes de liberar os fontes
        reg_resultado = self.alocar_reg(eh_float=eh_float)
        linha = f"{kw} {reg_resultado}, {reg_a}, {reg_b}"

        # libera os registradores de entrada — literais e temporários
        self.liberar_reg(reg_a)
        self.liberar_reg(reg_b)

        # remove entradas temporárias do dicionário
        if a.tipo == TipoToken.MEMORIA:
            self.memoria.pop(a.valor, None)
        if b.tipo == TipoToken.MEMORIA:
            self.memoria.pop(b.valor, None)

        # registra o resultado com chave única
        tmp_key = f"tmp_{self.tmp_counter}"
        self.tmp_counter += 1
        self.memoria[tmp_key] = reg_resultado

        self.codigo_assembly.append(header)
        self.codigo_assembly.append(linha)

        return Token(TipoToken.MEMORIA, tmp_key, self.current_line, operacao.coluna)

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

print("\n==== TESTE FLOAT ====\n")

tokens_float = [
    Token(TipoToken.NUMERO_REAL, "10.0", 1, 1),
    Token(TipoToken.NUMERO_REAL, "3.0", 1, 5),
    Token(TipoToken.OPERADOR, "/", 1, 9),
]

gerador = geradorAssembly()
print(gerador.gerarAssembly(tokens_float))