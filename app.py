from flask import Flask
from flask import render_template,request,redirect,url_for,flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from pymysql import cursors
import pymysql
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key="Develoteca"
def obtener_conexion():
    return pymysql.connect(host='localhost',
                                user='root',
                                password='',
                                db='sistema')
CARPETA = os.path.join('uploads')
app.config['CARPETA']= CARPETA  

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/')
def index():

    conn= obtener_conexion()
    cursor= conn.cursor()
    sql = "SELECT * FROM `empleados`;"
    cursor.execute(sql)
    empleados=cursor.fetchall()
    
    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)  
    
@app.route('/destroy/<int:id>')
def destroy(id):
        conn= obtener_conexion()
        cursor= conn.cursor()  
        
        cursor.execute("SELECT foto FROM empleados WHERE id=%s",(id))
        Fila = cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'],Fila[0][0]))

        cursor.execute("DELETE FROM empleados WHERE id=%s",(id))
        conn.commit()
        conn.close()
        return redirect('/')
    
@app.route('/edit/<int:id>')
def edit(id):
    conn= obtener_conexion()
    cursor= conn.cursor()  
    
    cursor.execute("SELECT * FROM empleados WHERE id=%s",(id))
    empleados=cursor.fetchall()
 
    return render_template('empleados/edit.html',empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre=request.form['txtnombre']
    _correo=request.form['txtcorreo']
    _foto=request.files['txtfoto']
    id=request.form['txtID']

    conn= obtener_conexion()
    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s;"
    datos=(_nombre,_correo,id)
    conn= obtener_conexion()
    cursor= conn.cursor()

    now = datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if _foto.filename!='':
        
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id=%s",(id))
        Fila = cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'],Fila[0][0]))

        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()
        
    cursor.execute(sql,datos)
    conn.commit()
    

    return redirect('/')

@app.route('/create')
def create():
    return render_template('empleados/create.html')



@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['txtnombre']
    _correo=request.form['txtcorreo']
    _foto=request.files['txtfoto']

    if _nombre=='' or _correo=='' or _foto=='':
        flash('Llena los campos')
        return redirect(url_for('create'))


    now = datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    conn= obtener_conexion()
    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s,%s,%s);"
    datos=(_nombre,_correo,nuevoNombreFoto)
    
    cursor= conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    
    app.run(debug=True)