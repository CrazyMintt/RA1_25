.section .data
num_0: .double 3.14
num_1: .double 2.0
num_2: .double 10.00
num_3: .double 10.0
num_4: .double 4.0
num_5: .double 10.00
num_6: .double 3.0
num_7: .double 4.0
num_8: .double 10.00
num_9: .double 15.0
num_10: .double 4.0
num_11: .double 10.00
num_12: .double 17.0
num_13: .double 5.0
num_14: .double 17.0
num_15: .double 5.0
num_16: .double 3.0
num_17: .double 2.0
num_18: .double 4.0
num_19: .double 1.0
num_20: .double 10.00
num_21: .double 10.00
num_22: .double 2.00
num_23: .double 7.5
num_24: .double 10.00
num_25: .double 2.0
num_26: .double 10.00
num_27: .double 10.00
num_28: .double 2.0
num_29: .double 3.0
num_30: .double 10.00
num_31: .double 10.00
num_32: .double 5.0
num_33: .double 2.0
num_34: .double 3.0
num_35: .double 2.0

.section .text
.global _start
_start:
LDR R12, =num_0
VLDR D2, [R12]
LDR R12, =num_1
VLDR D3, [R12]

VADD.F64 D4, D2, D3
LDR R12, =num_2
VLDR D0, [R12]
VMUL.F64 D0, D4, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
LDR R12, =num_3
VLDR D4, [R12]
LDR R12, =num_4
VLDR D3, [R12]

VSUB.F64 D2, D4, D3
LDR R12, =num_5
VLDR D0, [R12]
VMUL.F64 D0, D2, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
LDR R12, =num_6
VLDR D2, [R12]
LDR R12, =num_7
VLDR D3, [R12]

VMUL.F64 D4, D2, D3
LDR R12, =num_8
VLDR D0, [R12]
VMUL.F64 D0, D4, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
LDR R12, =num_9
VLDR D4, [R12]
LDR R12, =num_10
VLDR D3, [R12]

VDIV.F64 D2, D4, D3
LDR R12, =num_11
VLDR D0, [R12]
VMUL.F64 D0, D2, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
LDR R12, =num_12
VLDR D2, [R12]
LDR R12, =num_13
VLDR D3, [R12]

VDIV.F64 D4, D2, D3
vcvt.s32.f64 s0, D4
vmov R1, s0
MOV R12, R1
MOV R0, #10
MUL R0, R12, R0
BL __jtag_print_1dec
LDR R12, =num_14
VLDR D3, [R12]
LDR R12, =num_15
VLDR D2, [R12]

VDIV.F64 D4, D3, D2
vcvt.s32.f64 s0, D4
vmov R1, s0
vcvt.s32.f64 s0, D3
vmov R2, s0
vcvt.s32.f64 s0, D2
vmov R3, s0
MUL R4, R1, R3
SUB R4, R2, R4
MOV R12, R4
MOV R0, #10
MUL R0, R12, R0
BL __jtag_print_1dec
MOV R3, #2
MOV R2, #8

MOV R4, #1
pow_loop_6:
CMP R2, #0
BEQ pow_end_6
MUL R4, R4, R3
SUB R2, R2, #1
B pow_loop_6
pow_end_6:
MOV R12, R4
MOV R0, #10
MUL R0, R12, R0
BL __jtag_print_1dec
LDR R12, =num_16
VLDR D2, [R12]
LDR R12, =num_17
VLDR D3, [R12]

VADD.F64 D4, D2, D3
LDR R12, =num_18
VLDR D3, [R12]
LDR R12, =num_19
VLDR D2, [R12]

VSUB.F64 D5, D3, D2

VMUL.F64 D2, D4, D5
LDR R12, =num_20
VLDR D0, [R12]
VMUL.F64 D0, D2, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
LDR R12, =num_21
VLDR D2, [R12]
LDR R12, =num_22
VLDR D5, [R12]

VDIV.F64 D4, D2, D5
vcvt.s32.f64 s0, D4
vmov R4, s0
MOV R2, #3
MOV R3, #1

ADD R1, R2, R3

MOV R3, #1
pow_loop_12:
CMP R1, #0
BEQ pow_end_12
MUL R3, R3, R4
SUB R1, R1, #1
B pow_loop_12
pow_end_12:
MOV R12, R3
MOV R0, #10
MUL R0, R12, R0
BL __jtag_print_1dec
LDR R12, =num_23
VLDR D5, [R12]
VMOV.F64 D2, D5
LDR R12, =num_24
VLDR D0, [R12]
VMUL.F64 D0, D2, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
LDR R12, =num_25
VLDR D2, [R12]

VADD.F64 D4, D5, D2
VMOV.F64 D1, D4
LDR R12, =num_26
VLDR D0, [R12]
VMUL.F64 D0, D1, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
VMOV.F64 D4, D1
VMOV.F64 D2, D4
LDR R12, =num_27
VLDR D0, [R12]
VMUL.F64 D0, D2, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
LDR R12, =num_28
VLDR D4, [R12]
LDR R12, =num_29
VLDR D3, [R12]

VMUL.F64 D6, D4, D3
VMOV.F64 D3, D6
VMOV.F64 D4, D3
LDR R12, =num_30
VLDR D0, [R12]
VMUL.F64 D0, D4, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
VMOV.F64 D4, D2

VADD.F64 D6, D3, D4
LDR R12, =num_31
VLDR D0, [R12]
VMUL.F64 D0, D6, D0
VCVT.S32.F64 s0, D0
VMOV R0, s0
BL __jtag_print_1dec
LDR R12, =num_32
VLDR D6, [R12]
LDR R12, =num_33
VLDR D4, [R12]

VDIV.F64 D7, D6, D4
vcvt.s32.f64 s0, D7
vmov R3, s0
LDR R12, =num_34
VLDR D4, [R12]
LDR R12, =num_35
VLDR D6, [R12]

VDIV.F64 D7, D4, D6
vcvt.s32.f64 s0, D7
vmov R1, s0
vcvt.s32.f64 s0, D4
vmov R4, s0
vcvt.s32.f64 s0, D6
vmov R2, s0
MUL R5, R1, R2
SUB R5, R4, R5

SUB R2, R3, R5
MOV R12, R2
MOV R0, #10
MUL R0, R12, R0
BL __jtag_print_1dec
fim:
B fim
__jtag_putchar:
__jpch_wait:
    LDR  R12, [R1, #4]
    LSRS R12, R12, #16
    BEQ  __jpch_wait
    STR  R6, [R1]
    BX   LR
__jtag_print_1dec:
    PUSH {R1, R2, R3, R4, R5, R6, LR}
    LDR  R1, =0xFF201000
    CMP  R0, #0
    BGE  __jpd1_pos
    MOV  R6, #0x2D
    BL   __jtag_putchar
    RSB  R0, R0, #0
__jpd1_pos:
    MOV  R4, #0
    MOV  R3, #0
    MOV  R2, R0
__jpd1_div10:
    CMP  R2, #10
    BLT  __jpd1_div10_end
    SUB  R2, R2, #10
    ADD  R3, R3, #1
    B    __jpd1_div10
__jpd1_div10_end:
    PUSH {R2}
    MOV  R0, R3
    CMP  R0, #0
    BNE  __jpd1_iloop
    MOV  R6, #0x30
    BL   __jtag_putchar
    B    __jpd1_dot
__jpd1_iloop:
    MOV  R3, #0
    MOV  R2, R0
__jpd1_idiv:
    CMP  R2, #10
    BLT  __jpd1_idiv_end
    SUB  R2, R2, #10
    ADD  R3, R3, #1
    B    __jpd1_idiv
__jpd1_idiv_end:
    ADD  R5, R2, #0x30
    PUSH {R5}
    ADD  R4, R4, #1
    MOV  R0, R3
    CMP  R0, #0
    BNE  __jpd1_iloop
    MOV  R3, R4
__jpd1_iprint:
    POP  {R5}
    MOV  R6, R5
    BL   __jtag_putchar
    SUBS R3, R3, #1
    BNE  __jpd1_iprint
__jpd1_dot:
    MOV  R6, #0x2E
    BL   __jtag_putchar
    POP  {R5}
    ADD  R5, R5, #0x30
    MOV  R6, R5
    BL   __jtag_putchar
    MOV  R6, #0x0A
    BL   __jtag_putchar
    POP  {R1, R2, R3, R4, R5, R6, LR}
    BX   LR
