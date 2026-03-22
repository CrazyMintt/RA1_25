from parseExpressao import Token, TipoToken

class geradorAssembly():
    def __init__(self):
        self.memoria = {}
        self.pilha = []
        self.codigo_assembly = []
        self.current_line = 0
    def gerarAssembly(self,tokens:list[Token])->str: 
        for token in tokens:
            if token.linha != self.current_line:
                pilha = []
                self.current_line = token.linha
            if token.tipo == TipoToken.OPERADOR:
                b = self.pilha.pop()
                a = self.pilha.pop()
                criar_op_line_assembly(a,b,token)
                pass
            elif token.tipo != TipoToken.PARENTESE_DIR and token.tipo != TipoToken.PARENTESE_ESQ:
                self.append(token)
            

    def get_assembly_keyworld(operacao:Token):
        if operacao.valor == "+":
            return "ADD"
        if operacao.valor == "-":
            return "SUB"
        if operacao.valor == "*":
            return "MUL"
        if operacao.valor == "/":
            return 'VDIV.F32'

    def create_op_headers(a,b,operacao):
        header = ""
        
        if a.tipo == TipoToken.NUMERO_REAL:
            header += """
                .section .data\n
                num: .float 3.12\n
                LDR R12, =num\n
                VLDR S1, [R12]\n
            """
        elif a.tipo == TipoToken.NUMERO_INTEIRO:
            header += f"MOV R0,#{a.valor}\n"
        elif a.tipo == TipoToken.MEMORIA:
            self.header.get("")
            header
    def criar_op_line_assembly(a,b,operacao):
        kw = get_assembly_keyworld()
        create_op_headers()