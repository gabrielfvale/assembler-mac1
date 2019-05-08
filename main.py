import sys

commands = {
    'nop': 0x01, 
    'iadd': 0x02, 
    'isub': 0x05, 
    'iand': 0x08, 
    'ior': 0x0B,
    'dup': 0x0E,
    'pop': 0x10,
    'swap': 0x13,
    'bipush': 0x19,
    'iload': 0x1C, 
    'istore': 0x22,
    'wide': 0x28,
    'ldc_w': 0x32,
    'iinc': 0x36,
    'goto': 0x3C, 
    'iflt': 0x43,
    'ifeq': 0x47,
    'if_icmpeq': 0x4B,
    'invokevirtual': 0x55,
    'ireturn': 0x6B
}


def colorize(msg, color):
  final_msg = ''
  if color == 'RED':
    final_msg += '\033[0;37;41m %s \033[0m' % msg
  elif color == 'GREEN':
    final_msg += '\033[0;37;42m %s \033[0m' % msg
  return final_msg


def syntax_check(program):
  hinted_code = ''
  i = 0
  syntax_ok = True
  for line in program:
    i += 1
    if len(line) == 1:
      if line[0] not in commands:
        syntax_ok = False
        hinted_code += '{} Linha {}: comando inválido\n   {}\n'.format(colorize('ERROR', 'RED'), i, *line)
    if len(line) == 2:
      if line[0] not in commands:
        syntax_ok = False
        hinted_code += '{} Linha {}: comando inválido\n   {} {}\n'.format(colorize('ERROR', 'RED'), i, *line)
    elif len(line) == 3:
      if line[1] not in commands:
        syntax_ok = False
        hinted_code += '{} Linha {}: comando inválido\n{} {} {}\n'.format(colorize('ERROR', 'RED'), i, *line)
  print(hinted_code)
  return syntax_ok


def init(byte_array, num_of_vars):
  regs = [
    0x7300, # INIT
    0x0006, # CPP
    0x1001, # LV
    0x0400, # PC
    0x1001 + num_of_vars # SP
  ]

  regs = [[reg & 0xff, (reg >> 8) & 0xff] for reg in regs]
  for reg in regs:
    for reg_byte in reg:
      byte_array.append(reg_byte)
    byte_array.append(00)
    byte_array.append(00)


def write_output(byte_list):
  # Converte o array de bytes em bytes
  final_bytes = bytes(byte_list)

  # Escreve o arquivo final
  filename = sys.argv[1].split('.')[0] + '.exe'
  with open(filename, 'wb') as binary_output:
    # Write text or bytes to the file
    bytes_written = binary_output.write(final_bytes)
    print(colorize(filename, 'GREEN'))
    print('Foram escritos %d bytes.' % bytes_written)


def assemble(program):
  labels = {}
  byte_counter = 0
  # Cast bytes to bytearray
  byte_list = bytearray(b'\x00\x00\x00\x00')
  vars = []

  # Identifica as labels
  for line in program:
    # Encontra cada label no programa
    if len(line) > 2 and line[0] not in commands:
      labels[line[0]] = 0
    byte_counter += len(line)

  print('Q:', 20 + byte_counter)

  byte_counter = 0

  # Contador de vars e cálculo da distância de labels
  for line in program:
    # Primeiro caso: linha possui operador e operando, sendo o último uma var ou um int
    if len(line) == 2 and line[1] not in labels:
      if not line[1].isnumeric() and line[1] not in vars:
        vars.append(line[1])
      byte_counter += len(line)
    # Segundo caso: linha possui operador e label
    elif len(line) == 2 and line[1] in labels:
      labels[line[1]] = byte_counter + 1
      byte_counter += len(line) + 1
    # Terceiro caso: linha possui label, operador e operando
    elif len(line) == 3 and line[0] in labels:
      # Cálculo da distância entre labels
      labels[line[0]] = byte_counter + 1 - labels[line[0]]
      del line[0]
      byte_counter += len(line)
    else:
      byte_counter += len(line)

  # 20 bytes de inicialização
  init(byte_list, len(vars))

  for line in program:
    mic_fix = ['goto', 'if_icmpeq', 'iflt', 'ifeq']
    # Adiciona o comando a lista de bytes
    byte_list.append(commands[line[0]])

    if len(line) > 1:
      if line[1] in vars:
        # Adiciona a variavel a lista de bytes
        byte_list.append(vars.index(line[1]))
      elif line[1].isnumeric():
        # Adiciona o valor a lista de bytes
        byte_list.append(int(line[1]))
      elif line[1] in labels:
          label = labels[line[1]]
          # Checa se é necessário fazer fix de little-endian
          if line[0] in mic_fix:
            part1 = (label >> 8) & 0xff
            part2 = label & 0xff
          else:
            part1 = label & 0xff
            part2 = (label >> 8) & 0xff
          # Adiciona ambos os bytes da label
          byte_list.append(part1)
          byte_list.append(part2)
  write_output(byte_list)


def main():
  program = []

  with open(sys.argv[1], 'r') as program:
    program = [line.split() for line in program]

  if syntax_check(program):
    assemble(program)

main()
