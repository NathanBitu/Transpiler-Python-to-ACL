import warnings
warnings.filterwarnings("ignore")

### REGEX
import re

delimiter = '\n'
int_regex = re.compile(r'^[0-9]+$')
float_regex = re.compile(r'^[0-9]+\.[0-9]+$')
string_regex = re.compile(r'^\"[a-zA-Z0-9\ \_]*\"$')

function_regex = re.compile(r'^[A-Z]+\(\"{0,1}[A-Za-z0-9\_]*\"{0,1}\)$')

position_regex_integers = re.compile(r"^[0-9]{0,5}$")
position_regex_strings = re.compile(r"^[0-9a-zA-Z]{0,5}$")

valor = 'DELAY('

if function_regex.match(valor) != None:
    print('Certo')

### Tabela de Simbolos e palavras Reservadas
import pandas as pd

variable_table = pd.DataFrame(columns = ['label', 'type', 'value'])
palavras_reservadas = ['PRINT', 'DEFINE', 'SET', 'MOVE', 'DELAY', 'OPEN', 'CLOSE']

### Functions
def SET(args):
    global variable_table
    value = args.split('=')[1]
    label = args.split('=')[0]

    type = variable_table.loc[variable_table['label'] == label]['type']#.values[0]


    if len(type) == 0:
        return DEFINE(args)
    
    type = type.values[0]

    if type != 'Unknown':
        if type == 'int':
            if int_regex.match(value) != None:
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'value'] = value
                return ['SET {}={}'.format(label, value)]
            else:
                return ['ERRO SET']
        
        elif type == 'float':
            if float_regex.match(value) != None:
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'value'] = value
                return ['SET {}={}'.format(label, value)]
            else:
                return ['ERRO SET']

        elif type == 'string':
            if string_regex.match(value) != None:
                value = value.replace('"', '')[0:10]
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'value'] = '"{}"'.format(value)
                return []
            else:
                return ['ERRO SET']

    else:
            if int_regex.match(value) != None:
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'type'] = 'int'
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'value'] = value
                return ['SET {}={}'.format(label, value)]
        
            elif float_regex.match(value) != None:
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'type'] = 'float'
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'value'] = value
                return ['SET {}={}'.format(label, value)]

            elif string_regex.match(value) != None:
                value = value.replace('"', '')[0:10]
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'type'] = 'string'
                variable_table.at[variable_table.loc[variable_table['label'] == label].index.values[0], 'value'] = '"{}"'.format(value)
                return []
            else:
                return ['ERRO SET']

def DEFINE(args):
    global variable_table
    if '=' in args:      
        value = args.split('=')[1]
        label = args.split('=')[0]
        if int_regex.match(value) != None:
            variable_table = variable_table.append(pd.DataFrame({'label':[label], 'type':['int'], 'value': None}), ignore_index= True)
            return ['DEFINE {}'.format(label), SET(args)]

        elif float_regex.match(value) != None:
            variable_table = variable_table.append(pd.DataFrame({'label':[label], 'type':['float'], 'value': None}), ignore_index= True)
            return ['DEFINE {}'.format(label), SET(args)]

        elif string_regex.match(value) != None:
            variable_table = variable_table.append(pd.DataFrame({'label':[label], 'type':['string'], 'value': None}), ignore_index= True)
            SET(args)
            return []
        else:
            return ['ERRO DEFINE']
    elif args != None and type(args) == str:
        variable_table = variable_table.append(pd.DataFrame({'label':[args], 'type':['Unknown'], 'value': None}), ignore_index= True)
        return ['DEFINE {}'.format(args)]
        
    else:
        return ['ERRO DEFINE']

def PRINT(args):
    if string_regex.match(args) != None:
        value = args.replace('"', '')[0:10]
        return 'PRINT "{}"'.format(value)
    
    value = variable_table.loc[variable_table['label'] == args]['value']

    if len(value) != 0:
        return 'PRINT {}'.format(value.values[0])
    else:
        return "ERRO PRINT"

def MOVE(args):
    if position_regex_integers.match(args) != None:
        return 'MOVE {}'.format(args)
    elif position_regex_strings.match(args) != None:
        return 'MOVE {}'.format(args)
    else:
        return "ERRO MOVE"

def OPEN():
    return 'OPEN'

def CLOSE():
    return 'CLOSE'


def DELAY(args):
    if int_regex.match(args) != None:
        return 'DELAY {}'.format(args)
        
    type = variable_table.loc[variable_table['label'] == args]['type']
    value = variable_table.loc[variable_table['label'] == args]['value']

    if len(type) != 0:
        if type.values[0] != 'int':
            return 'ERRO DELAY'
        else:
            return 'DELAY {}'.format(value.values[0])
    
    else:
        return 'ERRO DELAY'
    
### Lendo código Python e transformando em ACL
with open('Python_program.txt', 'r', encoding='utf8') as f:
    lines = f.readlines()
    lista2 = list(map(lambda x: x.replace('\n', ''), lines))

transpiled_code = []

for line in lista2:
    if line == '':
        continue
    line = line.replace(' ', '')
    if line[0] == '#':
        continue
    if '=' in line:
        transpiled_code.append(SET(line))
        if "ERRO SET" in transpiled_code[-1] or "ERRO DEFINE" in transpiled_code[-1]:
            break
    elif function_regex.match(line) != None:
        func = line.split('(')[0]
        args = line.split('(')[1]
        args = args.split(')')[0]

        if func in palavras_reservadas:
            if func == "OPEN":
                transpiled_code.append([OPEN()])
            elif func == "CLOSE":
                transpiled_code.append([CLOSE()])
            elif func == "MOVE":
                transpiled_code.append([MOVE(args)])
                if "ERRO MOVE" in transpiled_code[-1]:
                    break
            elif func == 'PRINT':
                transpiled_code.append([PRINT(args)])
                if  "ERRO PRINT" in transpiled_code[-1]:
                    break
            elif func == 'DELAY':
                transpiled_code.append([DELAY(args)])
                if "ERRO DELAY" in transpiled_code[-1]:
                    break
        else:
            transpiled_code.append("Funcao não reconhecida")
            break
        
### Escrevendo novo arquivo com o código ACL
for i in transpiled_code[-1]:
    if 'ERRO' in i:
        print(i)
    
erro = False
for i in transpiled_code[-1]:
    if "ERRO" in i:
        with open('ACL_program.txt', 'w') as f:
            f.write("{} na linha: {}".format(i, len(transpiled_code)))
            erro = True

if not erro:
    with open('ACL_program.txt', 'w') as f:
        for i in transpiled_code:
            if len(i) != 0:
                for j in i:
                    if type(j) == list:
                        for k in j:
                            f.write(k)
                            f.write('\n')
                            continue
                    else:
                        if len(j) == 0:
                            continue
                        f.write(j)
                        f.write('\n')

### Debugging
print(variable_table)