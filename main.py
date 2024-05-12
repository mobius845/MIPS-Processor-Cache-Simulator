def hexBin(hex):
  return format(int(hex, 16), '032b')


def print_registers(reg):
  print("Registers:")
  for i in range(0, 32, 4):  # Print 4 registers per line
    print(
        f"${i:2}: {reg[f'${i}']:10} | ${i+1:2}: {reg[f'${i+1}']:10} | ${i+2:2}: {reg[f'${i+2}']:10} | ${i+3:2}: {reg[f'${i+3}']:10}"
    )
  print()


def print_memory(memory):
  print("Memory:")

  # Find the range of memory addresses to display
  non_zero_addresses = [
      address for address, value in memory.items() if value != 0
  ]
  if not non_zero_addresses:
    print("\nAll memory values are 0.\n")
    return

  min_address = min(non_zero_addresses)
  max_address = max(non_zero_addresses)

  # Align the start address to the nearest multiple of 4 less than or equal to min_address
  start_address = min_address - (min_address % 4)

  # Make sure we display at least 32 addresses (8 rows of 4 addresses each)
  while max_address - start_address < 32 * 4:
    max_address += 4

  # Print the memory values
  for address in range(start_address, max_address + 1,
                       16):  # Increment by 16 to get every 4 addresses
    for offset in range(0, 16, 4):  # Show 4 addresses per line
      current_address = address + offset
      value = memory.get(current_address, 0)
      print(f"M[{current_address:5}]: {value:10}", end=" | ")
    print()  # Newline at the end of each line of 4 addresses

  print()


def toAsm(mc, asm):
  op = {
      "001000": "addi",
      "000100": "beq",
      "000101": "bne",
      "000010": "j",
      "100011": "lw",
      "101011": "sw",
  }

  functs = {
      "100100": "and",
      '000000': 'sll',
      '000010': 'srl',
      '100010': 'sub',
      '101010': 'slt',
      "100000": 'add',
      '100110': 'xor',
      "111111": "calc",
  }

  opcode = mc[:6]

  #r-types
  if opcode == '000000':
    rs = mc[6:11]
    rt = mc[11:16]
    rd = mc[16:21]
    shamt = mc[21:26]
    funct = mc[26:]

    if funct in functs:
      if funct == '000000' or funct == '000010':
        asm.append(
            f"{functs[funct]} ${int(rd,2)}, ${int(rt,2)}, {int(shamt,2)}")
      elif funct == '111111':
        asm.append(f"{functs[funct]} ${int(rd,2)}, ${int(rs,2)}")
      else:
        asm.append(f"{functs[funct]} ${int(rd,2)}, ${int(rs,2)}, ${int(rt,2)}")

  #i-types
  elif opcode in op:
    rs = mc[6:11]
    rt = mc[11:16]
    imm0 = mc[16:]
    imm = int(imm0, 2)

    if imm0[0] == '1':
      imm -= 1 << len(imm0)

    if opcode == '100011' or opcode == '101011':
      asm.append(f"{op[opcode]} ${int(rt, 2)}, {imm}(${int(rs, 2)})")

    elif opcode == '000010':
      asm.append(f"{op[opcode]} {imm}")

    else:
      asm.append(f"{op[opcode]} ${int(rt,2)}, ${int(rs,2)}, {imm}")

##########################################################################
##                               CACHE                                  ##
##########################################################################

#cache initial variables
offset = 0
hit = 0
miss = 0
cacheCount = 0
idxbit = 0


block = [
  [0, 0],
  [0, 0],
  [0, 0],
  [0, 0],
  [0, 0],
  [0, 0],
  [0, 0],
  [0, 0]
  ]

lru = None

def cacheConfig():
  import os
  if os.path.exists("results.txt"):
      os.remove("results.txt")

  log = open("results.txt", "a")
  config = input('Enter a cache configuration (a, b, c, or d):\n')
  global idxbit
  global block
  global offset
  global lru
  if config=='a':
      idxbit = 0
      block = [[0, 0]]  # Single block
      lru = [0]
      offset = 8  # Block size of 256 Bytes
      log.write('Cache Log, Single Block Cache, 1 block, 256 bytes per block\n')
  elif config=='b':
      idxbit = 3
      block = [[0, 0] for _ in range(8)]  # 8 blocks\
      lru = [0, 1, 2, 3, 4, 5, 6, 7]
      offset = 6  # Block size of 64 Bytes
      log.write('Cache Log, Direct Mapped, 8 blocks, 64 bytes per block\n')
  elif config=='c':
      idxbit = 0
      block = [[0, 0] for _ in range(4)]  # 4 blocks
      lru = [0, 1, 2, 3]
      offset = 7  # Block size of 128 Bytes
      log.write('Cache Log, Fully Associative, 4 blocks, 128 bytes per block\n')
  elif config=='d':
      idxbit = 2
      block = [[0, 0] for _ in range(8)]  # 8 blocks but 2-way set associative implies 4 sets
      lru = [0, 1, 2, 3, 4, 5, 6, 7]
      offset = 6  # Block size of 64 Bytes
      log.write('Cache Log, 2-Way Set Associative, 4 sets, 64 bytes per block\n')
  log.close()


def cache(imm, rs):
    log = open("results.txt", "a")
    global hit
    global miss
    global cacheCount
    cacheCount+=1
    addr = bin(imm + rs)[2:].zfill(32)
    if idxbit==0:
        tag = addr[:-offset]
        block_range = f'0-{len(block)-1}'
        print(f'({cacheCount})  Address:{hex(int(addr,2))}, (tag {hex(int(tag,2))})  block range {block_range}')
        log.write(f'\n({cacheCount})  Address:{hex(int(addr,2))}, (tag {hex(int(tag,2))})  block range {block_range}')

        for i in range(len(block)):
          if [tag,1] == block[i]:
              if i in lru:
                lru.insert(0, lru.pop(lru.index(i)))
              print(f'trying block {i} tag {hex(int(tag,2))} -- HIT\n')
              log.write(f'\ntrying block {i} tag {hex(int(tag,2))} -- HIT\n')
              log.write(f'Access offset: {addr[-offset:]}\n')
              log.write(f'Least Recently Used blocks: {lru[::-1]}\n')
              hit+=1
              return
          elif [0,0] == block[i]:
              index = block.index([0,0])
              if index in lru:
                lru.insert(0, lru.pop(lru.index(index)))
              block[index] = [tag,1]
              print(f'trying block {i} empty/invalid -- MISS\n')
              log.write(f'\ntrying block {i} empty/invalid -- MISS\n')
              log.write(f'Pull from memory block: {hex(int(tag,2))}\n')
              log.write(f'Least Recently Used blocks: {lru[::-1]}\n')
              miss+=1
              return
          else:
              print(f'trying block {i} tag {hex(int(block[i][0],2))} -- OCCUPIED')
              log.write(f'\ntrying block {i} tag {hex(int(block[i][0],2))} -- OCCUPIED')
        print(f'MISS due to FULL SET -- LRU replace block {lru[-1]}\n')
        log.write(f'\nMISS due to FULL SET -- LRU replace block {lru[-1]}\n')
        lru.insert(0, lru.pop(lru.index(lru[-1])))
        log.write(f'Pull from memory block: {hex(int(tag,2))}\n')
        log.write(f'Least Recently Used blocks: {lru[::-1]}\n')
        if lru[-1] < len(block):
          block[lru[-1]][0] = tag
        miss+=1
      
    else: 
      tag = addr[:-(idxbit+offset)]
      idx = addr[-(idxbit+offset):-offset]
      set_idx = int(idx, 2)

      blocks_per_set = len(block) // (2 ** idxbit)
      
      if blocks_per_set == 1:  # Direct Mapped cache
        block_range = f'{int(idx, 2)}-{int(idx, 2)}'
        print(f'({cacheCount})  Address:{hex(int(addr,2))}, (tag {hex(int(tag,2))})  block range {block_range}')
        log.write(f'\n({cacheCount})  Address:{hex(int(addr,2))}, (tag {hex(int(tag,2))})  block range {block_range}')

        if block[int(idx,2)][1]==1:
          if block[int(idx,2)][0]==tag:
            print(f'trying block {int(idx,2)} tag {hex(int(tag,2))} -- HIT\n')
            log.write(f'\ntrying block {int(idx,2)} tag {hex(int(tag,2))} -- HIT\n')
            log.write(f'Access offset: {addr[-offset:]}\n')
            hit+=1
          else:
            print(f'trying block {int(idx,2)} tag {hex(int(block[int(idx,2)][0],2))} -- OCCUPIED\n')
            print(f'MISS due to FULL SET -- LRU replace block {int(idx,2)}\n')
            log.write(f'\ntrying block {int(idx,2)} tag {hex(int(block[int(idx,2)][0],2))} -- OCCUPIED\n')
            log.write(f'MISS due to FULL SET -- LRU replace block {int(idx,2)}\n')
            log.write(f'Pull from memory block: {hex(int(tag,2))}\n')
            block[int(idx,2)][0]=tag
            miss+=1

        elif block[int(idx,2)][1]==0:
          print(f'trying block {int(idx,2)} empty/invalid -- MISS\n')
          log.write(f'\ntrying block {int(idx,2)} empty/invalid -- MISS\n')
          log.write(f'Pull from memory block: {hex(int(tag,2))}\n')
          block[int(idx,2)]=[tag, 1]
          miss+=1
      else: # set associate
        print(f'({cacheCount})  Address:{hex(int(addr,2))}, (tag {hex(int(tag,2))})  block range {int(idx,2)}')
        log.write(f'\n({cacheCount})  Address:{hex(int(addr,2))}, (tag {hex(int(tag,2))})  block range {int(idx,2)}')
        block1 = block[2*set_idx]  # Block 1 in the set
        block2 = block[2*set_idx+1]  # Block 2 in the set
      
      # Check both blocks in the set
        for i, current_block in enumerate([block1, block2]):
            if current_block[1] == 1 and current_block[0] == tag:  # Cache hit
                # Update LRU
                lru.insert(0, lru.pop(lru.index(2*set_idx+i)))
                print(f'trying block {2*set_idx+i} tag {hex(int(tag,2))} -- HIT\n')
                log.write(f'\ntrying block {2*set_idx+i} tag {hex(int(tag,2))} -- HIT\n')
                log.write(f'Access offset: {addr[-offset:]}\n')
                log.write(f'Least Recently Used blocks: {lru[::-1]}\n')
                hit+=1
                return
            elif current_block[1] == 0:  # Empty block, cache miss
                # Update block and LRU
                block[2*set_idx+i] = [tag, 1]
                lru.insert(0, lru.pop(lru.index(2*set_idx+i)))
                print(f'trying block {2*set_idx+i} empty/invalid -- MISS\n')
                log.write(f'\ntrying block {2*set_idx+i} empty/invalid -- MISS\n')
                log.write(f'Pull from memory block: {hex(int(tag,2))}\n')
                log.write(f'Least Recently Used blocks: {lru[::-1]}\n')
                miss+=1
                return
        
        # If code reaches here, it's a cache miss and the set is full
        # Replace block based on LRU
        lru_block_to_replace = lru[-1]
        block[lru_block_to_replace] = [tag, 1]
        lru.insert(0, lru.pop(lru.index(lru_block_to_replace)))
        print(f'MISS due to FULL SET -- LRU replace block {lru_block_to_replace}\n')
        log.write(f'\nMISS due to FULL SET -- LRU replace block {lru_block_to_replace}\n')
        log.write(f'Pull from memory block: {hex(int(tag,2))}\n')
        log.write(f'Least Recently Used blocks: {lru[::-1]}\n')
        miss+=1

##########################################################################
##                                SIM                                   ##
##########################################################################

def sim(inD, reg, memory, binList):
  PC = 0

  while PC in inD:
    #parse ASM into instructions/registers/immediate, execute
    curr = inD[PC]
    part = curr.replace(",", "").split(" ")

    if part[0] == 'addi':
      rs = int(reg[part[2]])
      imm = int(part[3])
      reg[part[1]] = rs + imm
      PC += 4

    if part[0] == 'beq':
      rs = reg[part[2]]
      rt = reg[part[1]]
      imm = int(part[3])
      if rs == rt:
        PC += (imm * 4) + 4
      else:
        PC += 4

    if part[0] == 'bne':
      rs = reg[part[2]]
      rt = reg[part[1]]
      imm = int(part[3])
      if rs != rt:
        PC += (imm * 4) + 4
      else:
        PC += 4

    if part[0] == 'j':
      imm = int(part[1])
      PC = (PC & 0xF0000000) | (imm << 2)

    if part[0] == 'lw':
      rt = part[1]
      imm, rs_reg = part[2].split('(')
      rs_reg = rs_reg[:-1]  # remove the closing parenthesis
      rs = int(reg[rs_reg])
      cache(int(imm), rs)
      mem_address = rs + int(imm)
      registers[rt] = memory[mem_address]
      PC += 4

    if part[0] == 'sw':
      rt = part[1]
      imm, rs_reg = part[2].split('(')
      rs_reg = rs_reg[:-1]  # remove the closing parenthesis
      rs = int(reg[rs_reg])
      cache(int(imm), rs)
      rt_val = int(reg[rt])
      mem_address = rs + int(imm)
      memory[mem_address] = rt_val
      PC += 4

    if part[0] == 'and':
      rs = int(reg[part[2]])
      rt = int(reg[part[3]])
      result = rs & rt
      reg[part[1]] = result
      PC += 4

    if part[0] == 'sll':
      rd = part[1]
      rt = int(reg[part[2]])
      shamt = int(part[3])
      reg[rd] = rt << shamt
      PC += 4

    if part[0] == 'srl':
      rd = part[1]
      rt = int(reg[part[2]]
               ) & 0xFFFFFFFF  # Ensure rt is treated as a non-negative number
      shamt = int(part[3])
      reg[rd] = rt >> shamt
      PC += 4

    if part[0] == 'xor':
      rs = int(reg[part[2]])
      rt = int(reg[part[3]])
      reg[part[1]] = rs ^ rt
      PC += 4

    if part[0] == 'sub':
      rs = int(reg[part[2]])
      rt = int(reg[part[3]])
      reg[part[1]] = rs - rt
      PC += 4

    if part[0] == 'slt':
      rs = int(reg[part[2]])
      rt = int(reg[part[3]])
      if rs < rt:
        reg[part[1]] = 1
      else:
        reg[part[1]] = 0
      PC += 4

    if part[0] == 'add':
      rs = int(reg[part[2]])
      rt = int(reg[part[3]])
      reg[part[1]] = rs + rt
      PC += 4



##########################################################################
##                                MAIN                                  ##
##########################################################################

print('Reading in hex code file into a list of strings...')
f = open('p4.txt')
hexList = f.readlines()
f.close()

#print('Building up a list of hexcode lines:')
for i in range(len(hexList)):
  hexList[i] = hexList[i].replace("\n", "")
  #print(hexList[i])

#print("\nTo binary")
binList = []
for i in range(len(hexList)):
  binList.append(hexBin(hexList[i]))

#for i in range(len(hexList)):
#print(binList[i])

#print("\nTo Assembly:")
asmList = []
for i in range(len(binList)):
  toAsm(binList[i], asmList)

for i in range(len(asmList)):
  print(asmList[i])

cacheConfig()
########
registers = {f"${i}": 0 for i in range(32)}

memory = {i: 0 for i in range(0, 10000)}

#######

PC = 0
iDict = {}

for i in asmList:
  iDict[PC] = i
  PC += 4

sim(iDict, registers, memory, binList)

log = open("results.txt", "a")


print(f'Cache Hits: {hit}, Cache Misses: {miss}, Cache Hit Rate: {round(hit/(hit+miss),2)*100}%')
log.write(f'\n\nCache Hits: {hit}, Cache Misses: {miss}, Cache Hit Rate: {round(hit/(hit+miss),2)*100}%')
log.close()