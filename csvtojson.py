import re

##Expressões regulares usadas
##Compile para facilitar o processo
lineSplit = re.compile(r'\n')
fileNameSplit = re.compile(r'.csv,?')
argSplit = re.compile(r'(?<=[A-Za-z]),|,(?=[A-Za-z])')
valueSplit = re.compile(r',')
funcSearch = re.compile(r'[A-Za-z]+\{([0-9]+),?([0-9]+)?\}:*([A-Za-z]+)?')
funcArgSplit = re.compile(r'\{')
stringListSearch = re.compile(r'[A-Za-z]')

def openCSV(fileName):

    with open(fileName,"r",encoding='utf-8') as csvFile:
        data = csvFile.read()
    
    return data

def csvDataToDict(data):
    # Separar os dados por linhas
    lines = re.split(lineSplit,data)
    # Remover a ultima linha (Vazia)
    lines.pop()
    # Separar os argumentos da primeira linha
    args = re.split(argSplit,lines.pop(0))
    # Lista para guardar os dicionários com a informação de cada linha
    listOfDict = []
    # Percorrer as linhas uma a uma e transformar os dados em dicionarios
    # Chave é o argumento e key o valor na linha 
    for linha in lines:
        # Separar os valores da linha
        linha = re.split(valueSplit,linha)
        # Dicionário vazio para guardar a informação da linha
        d = {}
        # Percorrer os argumentos para dar zip com os valores
        for i in range(len(args)):
            # Procurar se existe função de agregação ou lista
            # Devidir os argumentos
            if y := re.search(funcSearch,args[i]):
                # Numero menor ou unico de colunas
                N = y.group(1)
                # Número maximo de colunas
                M = y.group(2)
                # Função de agregação a ser aplicado ou None se não existir função
                func = y.group(3)
                # Lista para agregar os valores
                l = []

                # Definir o número total de colunas
                if M != None:
                    N = int(M) + i
                elif N != None:
                    N = int(N) + i
                
                # Adicionar as colunas não vazias à lista
                # Improve search string or int
                for x in range(i,N):
                    if re.search(stringListSearch,linha[0]):
                        l.append(linha.pop(0))
                    elif linha[0] != '': 
                        l.append(int(linha.pop(0)))
                    else: 
                        linha.pop(0)

                # Retirar o nome do campo com várias colunas
                newarg = re.split(funcArgSplit,args[i])

                if func != None:
                    # Preparar o argumento para ser adicionado ao dicionario Arg_func
                    newarg = str(newarg[0]) + '_' + str(func)
                    #Aplicar a função de agregação á lista
                    if func == 'sum':
                        d[newarg] = sum(l)
                    elif func == 'max':
                        d[newarg] = max(l)
                    elif func == 'min':
                        d[newarg] = min(l)
                    elif func == 'media':
                        d[newarg] = float(sum(l)/len(l))
                else:
                    # Preparar o argumento para ser adicionado ao dicionario Arg
                    newarg = str(newarg[0])
                    d[newarg] = l
            elif ',' not in args[i]:
                # Adicionar o argumento e valor ao dciionário {Arg:Valor}
                d[args[i]] = linha.pop(0)
        # Inserir o dicionário com as informações na lista
        listOfDict.append(d)
        
    return listOfDict

def writeToJson(data,file):
    
    with open(file, "w",encoding= 'utf-8') as jsonfile:
        jsonfile.write('[\n')
        
        for d in data:
            jsonfile.write("\t{\n")

            for index,pair in enumerate(d.items()):
          
                if type(pair[1]) == list:
                    jsonfile.write("\t\t\"" + str(pair[0]) + "\": [")
                    for i,elem in enumerate(pair[1]):
                        if type(elem) == int:
                            jsonfile.write(str(elem))
                        else:
                            jsonfile.write('"'+elem+'"')
                        if i != len(pair[1]) - 1:
                            jsonfile.write(',')
                    jsonfile.write("]")
                elif type(pair[1]) == int:
                    jsonfile.write("\t\t\"" + str(pair[0]) + "\": " + str(pair[1]))
                else:
                    jsonfile.write("\t\t\"" + str(pair[0]) + "\": \"" + str(pair[1]) + "\"")
                
                if index != len(d) - 1:
                    jsonfile.write(",\n")
                else:
                    jsonfile.write("\n")
                
            if d != data[-1]: 
                jsonfile.write("\t},\n")
            else: 
                jsonfile.write("\t}\n]")

    jsonfile.close()

def main():
    # Recebe o nome dos ficheiros CSV como input
    listOfFiles = re.split(fileNameSplit,input())
    # Remove o ultimo elemento que é vazio
    listOfFiles.pop()
    # Precorre a lista de ficheiros para os transformar em JSON
    for fileName in listOfFiles:
        data = openCSV(fileName + ".csv")
        data = csvDataToDict(data)
        writeToJson(data,fileName + ".json")

    print("Ficheiros convertidos!")

if __name__ == "__main__":
    main()