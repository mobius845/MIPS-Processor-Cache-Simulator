# P4 test program
addi $8, $0, 2
addi $9, $0, 120 # num of words to write in the dense array x 4
sw_loop: # write a dense array from high to low mem
sw $8, 0x2020($9)
beq $9, $0, sw_done
addi $9, $9, -4
#sub $8, $0, $8
addi $8, $8, 137
sub $8, $0, $8
xor $8, $8, $9
beq $0, $0, sw_loop
sw_done:
addi $8, $0, 0x2100 # beginning addr of sparse array
addi $9, $0, 0x2010 # beginning addr of dense array
addi $10, $0, 20 # num of items in the sparse array
addi $7, $0, 36 # initial sparsity.
outer_loop:
addi $14, $0, 3 # neighborhood size
lw $11, 0($9)
inner_loop:
lw $12, 0($9)
slt $13, $12, $11
beq $13, $0, skip
add $11, $0, $12
skip:
addi $9, $9, 4
addi $14, $14, -1
bne $14, $0, inner_loop
sw $11, 0($8) # store the min of neighborhood to sparse array
add $8, $8, $7 # next location of the sparse array item
addi $7, $7, 8 # increased sparsity
addi $9, $9, -8 # next neighborhood in dense array
addi $10, $10, -1 # count -1 for sparse array
slt $13, $10, $0
beq $13, $0, outer_loop
sw $13, 0($8) # final mark writing to mem