import requests
from bs4 import BeautifulSoup
import urllib3
import csv
import math

def tablaCarrera():
	http = urllib3.PoolManager()
	f = csv.writer(open("CARRERA.csv", "w"))
	fPlan = csv.writer(open("PLAN.csv", "w"))
	fGeneracion = csv.writer(open("GENERACION.csv","w"))
	f.writerow(["ID_CARRERA","NOMBRE"])
	fPlan.writerow(["ID_PLAN","ID_CARRERA","NOMBRE","CREDITOS_OBLIGATORIOS","CREDITOS_OPTATIVOS","ID_PLAN_BASE","ID_CARRERA_INTERNA","SEMESTRES_CURRICULARES","SEMESTRES_REGLAMENTARIOS","GENERACION"])
	fGeneracion.writerow(["ID_PLAN_GENERACION","ID_PLAN","GENERACION"])
	web = http.request('GET', 'http://servacad.ingenieria.unam.mx/~consumapa/mapas.php')
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
		f.writerow([ID_CARRERA[n],NOMBRE[n]])
		tablaPlan(ID_CARRERA[n],fPlan,fGeneracion)

def tablaPlan(ID_CARRERA,f,fGeneracion):
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
		web = http.request('GET', 'http://servacad.ingenieria.unam.mx/~consumapa/detalle_mapa.php?lacarrera='+ID_CARRERA+'&sumapa='+generacion)
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
					web = http.request('GET', 'http://www.dgae-siae.unam.mx/educacion/planes.php?acc=est&pde='+clave.get_text()+'&planop=1')
					soup = BeautifulSoup(web.data, 'lxml')
					tdPlan = soup.find_all('td')
					for registro in tdPlan:
						valor = registro.get_text()
						if valor.startswith("ING"):
							NOMBRE.append(valor)
					bPlan = soup.find_all('b')
					SEMESTRES_CURRICULARES.append(bPlan[9].get_text()[0:1])
					SEMESTRES_REGLAMENTARIOS.append(str(math.ceil(int(bPlan[9].get_text()[0:2])+(int(bPlan[9].get_text()[0:2])/2))))
					CREDITOS_OBLIGATORIOS.append(bPlan[11].getText())
					CREDITOS_OPTATIVOS.append(bPlan[12].getText())
					GENERACION.append(generacion)
	for n in range(len(ID_PLAN)):
		print(ID_PLAN[n]+","+ID_CARRERA,NOMBRE[n]+","+CREDITOS_OBLIGATORIOS[n]+","+CREDITOS_OPTATIVOS[n]+","+""+","+SEMESTRES_CURRICULARES[n]+","+SEMESTRES_REGLAMENTARIOS[n])
		f.writerow([ID_PLAN[n],ID_CARRERA,NOMBRE[n],CREDITOS_OBLIGATORIOS[n],CREDITOS_OPTATIVOS[n],"","",SEMESTRES_CURRICULARES[n],SEMESTRES_REGLAMENTARIOS[n]])
		tablaGeneracion(ID_PLAN[n],GENERACION[n],fGeneracion)

def tablaGeneracion(ID_PLAN,GENERACION,FILE):
	ID_PLAN_GENERACION = ID_PLAN + GENERACION
	FILE.writerow([ID_PLAN_GENERACION,ID_PLAN,GENERACION])

def tablaSemestre(fSemestre):
	nombresSemestres=["NO APLICA","PRIMER","SENGUDO","TERCERO","CUARTO","QUINTO","SEXTO","SEPTIMO","OCTAVO","NOVENO","DECIMO"]
	numero = []
	for n in range(len(nombresSemestres)):
		fSemestre.writerow([n,nombresSemestres[n]])

def tablaEstructura(fEstructura, ID_PLAN):
	http = urllib3.PoolManager()
	web = http.request('GET', 'http://www.dgae-siae.unam.mx/educacion/planes.php?acc=est&pde=' + ID_PLAN + '&planop=1')
	soup = BeautifulSoup(web.data, 'lxml')
	asignaturas = soup.find_all('input')
	for asignatura in asignaturas:
		ID_CLAVE_ASIGNATURA = asignatura.get('value')
		name = asignatura.get('name')
		if str(name) == 'asg':
			print(ID_CLAVE_ASIGNATURA)
			web = http.request('GET', 'http://www.dgae-siae.unam.mx/educacion/asignaturas.php?ref=asgxpde&pde='+ ID_PLAN +'&asg='+ ID_CLAVE_ASIGNATURA)
			soup = BeautifulSoup(web.data, 'lxml')
			td = soup.find_all('td')
			for registro in td:
				clase = registro.get('class')
				if str(clase) == '[\'CellTit\']':
					

	

def main():
	#tablaCarrera()
	#fSemestre = csv.writer(open("SEMESTRE.csv","w"))
	fAsignatura = csv.writer(open("ASIGNATURA.csv","w"))
	#tablaSemestre(fSemestre)

	tablaEstructura(fAsignatura,"2040")

main()