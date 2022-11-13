import re
'''
Expressões regulares usadas
Compilar antes facilita a legibilidade do código
'''
# ER para separar as linhas do ficheiro
linhaSplit = re.compile(r'\n')
# ER para separar o nome dos ficheiros
nomeFicheiroSplit = re.compile(r'.csv,?')
# ER para separar os argumentos do cabeçalho
argSplit = re.compile(r'(?<=[A-Za-z]),|,(?=[A-Za-z])')
# ER para separar os valores das colunas de uma linha
valoresSplit = re.compile(r',')
# ER para procurar uma função de compreensão
funcSearch = re.compile(r'[A-Za-z]+\{([0-9]+),?([0-9]+)?\}:*([A-Za-z]+)?')
# ER para remover o nome da função em compreensão
funcArgSplit = re.compile(r'\{')
#ER para verificar se o valor é uma string ou um inteiro
listaStringSearch = re.compile(r'[A-Za-z]')


def openCSV(ficheiro):
    '''
    Lê um ficheiro CSV e guarda os seus dados num buffer
    :param ficheiro: Nome do ficheiro
    :return: Buffer com os dados do ficheiro
    '''

    with open(ficheiro, "r", encoding='utf-8') as ficheiroCSV:
        dados = ficheiroCSV.read()

    return dados


def csvDataToDict(dados):
    '''
    Converte o cabeçalho do ficheiro numa lista de argumentos
    Transforma cada linha num dicionário, onde a chave é o argumento e o valor a informação da coluna

    :param dados: Buffer com os dados do ficheiro
    :return: Resultado da conversão dos dados
    '''

    # Separar as linhas do ficheiro
    linhas = re.split(linhaSplit, dados)
    linhas.pop()

    # Retirar os argumentos do cabeçalho
    args = re.split(argSplit, linhas.pop(0))
    listaDeDic = []

    for linha in linhas:
        # Separar os valores da linha
        linha = re.split(valoresSplit, linha)

        d = {}
        # Percorrer os argumentos para dar zip com os valores
        for i in range(len(args)):
            # Procura se existe função de agregação ou lista
            if y := re.search(funcSearch, args[i]):
                N = y.group(1)
                M = y.group(2)
                # Função de agregação a ser aplicado ou None se não existir função
                func = y.group(3)
                l = []

                # Definir o número total de colunas
                if M != None:
                    N = int(M) + i
                elif N != None:
                    N = int(N) + i

                # Adicionar as colunas não vazias à lista
                for x in range(i, N):
                    if re.search(listaStringSearch, linha[0]):
                        l.append(linha.pop(0))
                    elif linha[0] != '':
                        l.append(int(linha.pop(0)))
                    else:
                        linha.pop(0)

                # Retirar o nome do campo com várias colunas
                novoarg = re.split(funcArgSplit, args[i])

                if func != None:
                    # Preparar o argumento para ser adicionado ao dicionario Arg_func
                    novoarg = str(novoarg[0]) + '_' + str(func)
                    # Aplicar a função de agregação á lista
                    if func == 'sum':
                        d[novoarg] = sum(l)
                    elif func == 'max':
                        d[novoarg] = max(l)
                    elif func == 'min':
                        d[novoarg] = min(l)
                    elif func == 'media':
                        d[novoarg] = float(sum(l)/len(l))
                else:
                    novoarg = str(novoarg[0])
                    d[novoarg] = l
            elif ',' not in args[i]:
                # Adicionar o argumento e valor ao dicionário {Arg:Valor}
                d[args[i]] = linha.pop(0)
        # Inserir o dicionário com as informações na lista
        listaDeDic.append(d)

    return listaDeDic


def writeToJson(dados, ficheiro):
    '''
    Função que percorre a lista de dicionários e escreve um a um no ficheiro JSON de output

    :param dados: Lista de dicionários com a informação
    :param ficheiro: Nome do ficheiro de output
    '''

    with open(ficheiro, "w", encoding='utf-8') as ficheiroJSON:
        ficheiroJSON.write('[\n')

        for d in dados:
            ficheiroJSON.write("\t{\n")

            for i, par in enumerate(d.items()):

                if type(par[1]) == list:
                    ficheiroJSON.write("\t\t\"" + str(par[0]) + "\": [")
                    for i, elem in enumerate(par[1]):
                        if type(elem) == int:
                            ficheiroJSON.write(str(elem))
                        else:
                            ficheiroJSON.write('"'+elem+'"')
                        if i != len(par[1]) - 1:
                            ficheiroJSON.write(',')
                    ficheiroJSON.write("]")
                elif type(par[1]) == int:
                    ficheiroJSON.write(
                        "\t\t\"" + str(par[0]) + "\": " + str(par[1]))
                else:
                    ficheiroJSON.write(
                        "\t\t\"" + str(par[0]) + "\": \"" + str(par[1]) + "\"")

                if i != len(d) - 1:
                    ficheiroJSON.write(",\n")
                else:
                    ficheiroJSON.write("\n")

            if d != dados[-1]:
                ficheiroJSON.write("\t},\n")
            else:
                ficheiroJSON.write("\t}\n]")

    ficheiroJSON.close()


def main():
    '''
    É recebido uma lista de ficheiros CSV como input.
    Os dados de cada ficheiro serão transformados numa lista de dicionários.
    Por fim estes dados serão convertidos e escritos num ficheiro JSON como output.
    '''

    listaDeFicheiros = re.split(nomeFicheiroSplit, input())
    listaDeFicheiros.pop()

    for ficheiro in listaDeFicheiros:
        dados = openCSV(ficheiro + ".csv")
        dados = csvDataToDict(dados)
        writeToJson(dados, ficheiro + ".json")

    print("Ficheiros convertidos!")


if __name__ == "__main__":
    main()
