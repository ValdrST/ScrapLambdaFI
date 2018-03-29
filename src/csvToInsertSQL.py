#encoding=utf8
import sys
import threading
def leerEstructuraCSV(CSV):
    f = open(CSV,"r")
    estructura = []
    for linea in f:
        estructura.append(linea)
    f.close()
    return estructura

def convertirEstructuraCSV(table, estructura):
    f = open("SQL/"+table + ".sql","w")
    #print("estructura"+table)
    query = "INSERT INTO "+ table +" ("
    columns = estructura[0]
    query = (query + columns + ") VALUES (")
    for values in estructura[1:]:
        valores = values.split(",")
        values = valores[0]
        for valor in valores[1:]:
            valor = valor.replace('\n','')
            if not valor.isnumeric():
                valor = '\''+ valor + '\''
            valor=valor.replace("\n","")
            values =values+", " + valor
        queryFinal = (query + values + ");").replace("\n","")
        f.write(queryFinal+"\n")
    f.close()


def generarSQL(tablas):
        #convertirEstructuraCSV(argumento[:punto],leerEstructuraCSV(str(argumento)))
        try:
            if "-A" in sys.argv:
                try:
                    argumentos = sys.argv[1:]
                    #print("Consola")
                    for argumento in argumentos:
                        punto = argumento.find(".")
                        thread = threading.Thread(target=convertirEstructuraCSV, args=(argumento[:punto],leerEstructuraCSV(str(argumento)),))
                        thread.start()
                except:
                    print("Archivo no valido")
            elif "-T" in sys.argv:
                #print("tablas")
                for argumento in tablas:
                    #print(argumento)
                    punto = argumento.find(".")
                    thread = threading.Thread(target=convertirEstructuraCSV, args=(argumento[:punto],leerEstructuraCSV(str(argumento)),))
                    thread.start()
                    thread.join()
        except:
                print("no definio argumentos")