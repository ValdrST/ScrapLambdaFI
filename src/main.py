import requests
from bs4 import BeautifulSoup
import urllib3
import csv
import math
import threading
from csvToInsertSQL import generarSQL
def tablaCarrera():
	http = urllib3.PoolManager()
	url = 'http://servacad.ingenieria.unam.mx/~consumapa/mapas.php'
	fCarrera = csv.writer(open("CARRERA.csv", "w"))
	fPlan = csv.writer(open("PLAN.csv", "w"))
	fGeneracion = csv.writer(open("GENERACION.csv","w"))
	fEstructura = csv.writer(open("ESTRUCTURA.csv","w"))
	fAsignatura = csv.writer(open("ASIGNATURA.csv","w"))
	fCarrera.writerow(["ID_CARRERA","NOMBRE"])
	fPlan.writerow(["ID_PLAN","ID_CARRERA","NOMBRE","CREDITOS_OBLIGATORIOS","CREDITOS_OPTATIVOS","ID_PLAN_BASE","ID_CARRERA_INTERNA","SEMESTRES_CURRICULARES","SEMESTRES_REGLAMENTARIOS"])
	fGeneracion.writerow(["ID_PLAN_GENERACION","ID_PLAN","GENERACION"])
	fEstructura.writerow(["ID_ESTRUCTURA","ID_PLAN","ID_ASIGNATURA","TIPO","ID_SEMESTRE","LABORATORIO"])
	fAsignatura.writerow(["ID_ASIGNATURA","NOMBRE","CREDITOS","HORAS","DEPARTAMENTO","OFICIAL"])
	web = http.request('GET', url)
	soup = BeautifulSoup(web.data, 'lxml')
	CARRERA = soup.find_all('td')
	ID_CARRERA=[]
	NOMBRE=[]
	for contenido in CARRERA:
		alineacion = contenido.get('align')
		clase = contenido.get('class')
		width = contenido.get('width')
		if str(alineacion) == 'center' and str(clase) == "[\'celda_contenido\']" and str(width) == "None":
			ID_CARRERA.append(contenido.get_text())
		if str(alineacion) == 'left' and str(clase) == "['celda_contenido\']":
			NOMBRE.append(contenido.get_text())
	for n in range(len(ID_CARRERA)):
		fCarrera.writerow([ID_CARRERA[n],NOMBRE[n]])
		thread = threading.Thread(target=tablaPlan, args=(ID_CARRERA[n],fPlan,fGeneracion, fEstructura, fAsignatura,))
		thread.start()
		#tablaPlan(ID_CARRERA[n],fPlan,fGeneracion, fEstructura, fAsignatura)

def tablaPlan(ID_CARRERA,f,fGeneracion, fEstructura, fAsignatura):
	http = urllib3.PoolManager()
	generaciones = ['2006','2009','2010','2016']
	ID_PLAN = []
	NOMBRE = []
	CREDITOS_OBLIGATORIOS = []
	CREDITOS_OPTATIVOS = []
	SEMESTRES_CURRICULARES = []
	SEMESTRES_REGLAMENTARIOS = []
	GENERACION = []
	for generacion in generaciones:
		url = 'http://servacad.ingenieria.unam.mx/~consumapa/detalle_mapa.php?lacarrera='+ID_CARRERA+'&sumapa='+generacion
		web = http.request('GET', url)
		soup = BeautifulSoup(web.data, 'lxml')
		span = soup.find_all('span')
		disponible = True
		for spaner in span:
			clase = spaner.get('class')
			if str(clase) == '[\'titulo2\']':
				disponible = False
		if disponible == True:
			TD = soup.find_all('td')
			for clave in TD:
				clase = clave.get('class')
				align = clave.get('align')
				valign = clave.get('valign')
				if str(clase) == '[\'celda_contenido_bis\']' and str(align) == 'center' and str(valign) == 'top' and len(str(clave.get_text()))==4:
					ID_PLAN.append(clave.get_text())
					url = 'http://www.dgae-siae.unam.mx/educacion/planes.php?acc=est&pde='+clave.get_text()+'&planop=1'
					web = http.request('GET', url)
					soup = BeautifulSoup(web.data, 'lxml')
					tdPlan = soup.find_all('td')
					for registro in tdPlan:
						valor = registro.get_text()
						clase = registro.get('class')
						if valor.startswith("ING") and str(clase) == '[\'CellTit\']' :
							NOMBRE.append(valor)
					bPlan = soup.find_all('b')
					SEMESTRES_CURRICULARES.append(str(int(bPlan[9].get_text()[0:2])))
					SEMESTRES_REGLAMENTARIOS.append(str(math.ceil(int(bPlan[9].get_text()[0:2])+(int(bPlan[9].get_text()[0:2])/2))))
					CREDITOS_OBLIGATORIOS.append(bPlan[11].getText())
					CREDITOS_OPTATIVOS.append(bPlan[12].getText())
					GENERACION.append(generacion)
	for n in range(len(ID_PLAN)):
		print(ID_PLAN[n]+","+ID_CARRERA,NOMBRE[n]+","+CREDITOS_OBLIGATORIOS[n]+","+CREDITOS_OPTATIVOS[n]+","+""+","+SEMESTRES_CURRICULARES[n]+","+SEMESTRES_REGLAMENTARIOS[n])
		f.writerow([ID_PLAN[n],ID_CARRERA,NOMBRE[n],CREDITOS_OBLIGATORIOS[n],CREDITOS_OPTATIVOS[n],"","",SEMESTRES_CURRICULARES[n],SEMESTRES_REGLAMENTARIOS[n]])
		tablaGeneracion(ID_PLAN[n],GENERACION[n],fGeneracion)
		thread = threading.Thread(target=tablaEstructura, args=(fEstructura,ID_PLAN[n],fAsignatura,))
		thread.start()
		#tablaEstructura(fEstructura,ID_PLAN[n],fAsignatura)

def tablaGeneracion(ID_PLAN,GENERACION,FILE):
	ID_PLAN_GENERACION = ID_PLAN + GENERACION
	FILE.writerow([ID_PLAN_GENERACION,ID_PLAN,GENERACION])

def tablaSemestre(fSemestre):
	nombresSemestres=["NO APLICA","PRIMER","SENGUDO","TERCERO","CUARTO","QUINTO","SEXTO","SEPTIMO","OCTAVO","NOVENO","DECIMO"]
	numero = []
	for n in range(len(nombresSemestres)):
		fSemestre.writerow([n,nombresSemestres[n]])

def tablaEstructura(fEstructura, ID_PLAN, fAsignatura):
	http = urllib3.PoolManager()
	url = 'http://www.dgae-siae.unam.mx/educacion/planes.php?acc=est&pde=' + ID_PLAN + '&planop=1'
	web = http.request('GET', url)
	soup = BeautifulSoup(web.data, 'lxml')
	asignaturas = soup.find_all('input')
	ID_ESTRUCTURA = []
	ID_ASIGNATURA = []
	ID_SEMESTRE = []
	TIPO = []
	NOMBRE = []
	CREDITOS = []
	HORAS = []
	for asignatura in asignaturas:
		
		name = asignatura.get('name')
		if str(name) == 'asg':
			ClaveAsignatura = asignatura.get('value')
			ID_ASIGNATURA.append(ClaveAsignatura)
			ID_ESTRUCTURA.append(ID_PLAN+ClaveAsignatura)
			url = 'http://www.dgae-siae.unam.mx/educacion/asignaturas.php?ref=asgxpde&pde='+ ID_PLAN +'&asg='+ ClaveAsignatura
			web = http.request('GET', url)
			soup = BeautifulSoup(web.data, 'lxml')
			td = soup.find_all('td')
			for registro in td:
				clase = registro.get('class')
				flag = False
				if str(clase) == '[\'CellTit\']':
					registroText = registro.get_text()
					if registroText == 'OBLIGATORIA' or registroText == 'OPTATIVA':
						flag = True
						TIPO.append(registroText[0:3])
						tipo = registroText[0:3]
					indiceSem = registroText.find('SEMESTRE')
					indiceCred = registroText.find('CREDITOS')
					if 	indiceSem != -1 and flag == False:
						if tipo == 'OBL':
							if registroText[0:indiceSem-1] == 'PRIMER':
								ID_SEMESTRE.append(1)
							elif registroText[0:indiceSem-1] == 'SEGUNDO':
								ID_SEMESTRE.append(2)
							elif registroText[0:indiceSem-1] == 'TERCER':
								ID_SEMESTRE.append(3)
							elif registroText[0:indiceSem-1] == 'CUARTO':
								ID_SEMESTRE.append(4)
							elif registroText[0:indiceSem-1] == 'QUINTO':
								ID_SEMESTRE.append(5)
							elif registroText[0:indiceSem-1] == 'SEXTO':
								ID_SEMESTRE.append(6)
							elif registroText[0:indiceSem-1] == 'SEPTIMO':
								ID_SEMESTRE.append(7)
							elif registroText[0:indiceSem-1] == 'OCTAVO':
								ID_SEMESTRE.append(8)
							elif registroText[0:indiceSem-1] == 'NOVENO':
								ID_SEMESTRE.append(9)
							elif registroText[0:indiceSem-1] == 'DECIMO':
								ID_SEMESTRE.append(10)
							else:
								ID_SEMESTRE.append(0)
						else:
							ID_SEMESTRE.append(0)
					elif indiceCred != -1:
						CREDITOS.append(registroText[0:indiceCred-1])
						HORAS.append(int(registroText[0:indiceCred-1])/2)
					elif flag == False:
						ID_SEMESTRE.append(0)
				elif str(clase) == '[\'CellSpa\']':
					colspan = registro.get('colspan')
					if colspan == '2':
						NOMBRE.append(registro.get_text())
	print(str(len(ID_ESTRUCTURA))+" "+str(len(ID_ASIGNATURA))+" "+str(len(TIPO))+" "+str(len(ID_SEMESTRE)))
	for n in range(len(ID_ESTRUCTURA)):
		fEstructura.writerow([ID_ESTRUCTURA[n],ID_PLAN,ID_ASIGNATURA[n],TIPO[n],ID_SEMESTRE[n],"0"])
		fAsignatura.writerow([ID_ASIGNATURA[n],NOMBRE[n],CREDITOS[n],HORAS[n],"0","1"])

def eliminarRepetidos(file):
	f = open(file,"r")
	columnNames = f.readline()
	listaChida = list(set(f))
	f2 = open(file,"w")
	f2.write(columnNames)
	for elemento in listaChida:
		f2.write(elemento)
	f.close()
	f2.close()



def main():
	tablas = ['ASIGNATURA.csv', 'CARRERA.csv', 'PLAN.csv', 'GENERACION.csv','SEMESTRE.csv','ESTRUCTURA.csv']
	#tablaCarrera()
	#fSemestre = csv.writer(open("SEMESTRE.csv","w"))
	#fSemestre.writerow(["ID_SEMESTRE", "NOMBRE"])
	#tablaSemestre(fSemestre)
	eliminarRepetidos("ASIGNATURA.csv")
	eliminarRepetidos("PLAN.csv")
	eliminarRepetidos("ESTRUCTURA.csv")
	eliminarRepetidos("GENERACION.csv")
	generarSQL(tablas)
	

	

main()