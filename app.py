from flask import Flask
from flask import render_template,request,redirect,url_for,flash
from flaskext.mysql import MySQL
from flask import send_from_directory 
from datetime import datetime
import os

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key="validations"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='127.0.0.1'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='employee-system'
mysql.init_app(app)

FOLDER = os.path.join('uploads')
app.config['FOLDER']=FOLDER

@app.route('/')
def index():
    sql = "SELECT * FROM `employees`;"
    
    conn = mysql.connect()
    cursor = conn.cursor() #donde se almacena la informacion
    cursor.execute(sql)
    employees=cursor.fetchall() #regresa la informacion y la guarda en employees

    conn.commit() #indica que la instrucción se terminó

    return render_template('index.html', employees=employees)

@app.route('/uploads/<namePhoto>')
def uploads(namePhoto):
    return send_from_directory(app.config['FOLDER'],namePhoto)

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/store', methods=['POST'])
def storage():
    _name=request.form['txtName']
    _mail=request.form['txtMail']
    _photo=request.files['txtPhoto']

    #validacion que los campos no estén vacios
    if _name=='' or _mail=='' or _photo=='':
        flash('The data cannot be empty')
        return redirect(url_for('create'))
    
    now = datetime.now()
    time = now.strftime("%Y%H%M%S")

    if _photo.filename!='':
        new_name_photo=time+_photo.filename
        _photo.save("uploads/"+new_name_photo)

    sql = "INSERT INTO `employees` (`id`, `name`, `mail`, `photo`) VALUES (NULL,%s,%s,%s);"
    
    data=(_name,_mail,new_name_photo)

    conn = mysql.connect()
    cursor = conn.cursor() #donde se almacena la informacion
    cursor.execute(sql, data)
    conn.commit() #indica que la instrucción se terminó

    return redirect('/')

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT photo FROM employees WHERE id=%s", id)
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['FOLDER'],fila[0][0]))

    cursor.execute("DELETE FROM employees WHERE id=%s",(id))
    conn.commit()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):

    conn = mysql.connect()
    cursor = conn.cursor() #donde se almacena la informacion
    cursor.execute('SELECT * FROM employees WHERE id=%s',(id))
    employees=cursor.fetchall()
    conn.commit()

    return render_template('edit.html',employees=employees)

@app.route('/update', methods=['POST'])
def update():
    _name=request.form['txtName']
    _mail=request.form['txtMail']
    _photo=request.files['txtPhoto']
    id=request.form['txtID']

    sql = "UPDATE `employees` SET `name`=%s, `mail`=%s WHERE id=%s;"
    
    data=(_name,_mail,id)

    conn = mysql.connect()
    cursor = conn.cursor() 

    now = datetime.now()
    time = now.strftime("%Y%H%M%S")

    if _photo.filename!='':
        new_name_photo=time+_photo.filename
        _photo.save("uploads/"+new_name_photo)

        cursor.execute("SELECT photo FROM employees WHERE id=%s", id)
        fila=cursor.fetchall()
        os.remove(os.path.join(app.config['FOLDER'],fila[0][0]))
        cursor.execute("UPDATE employees SET photo=%s WHERE id=%s",(new_name_photo,id))
        conn.commit()

    cursor.execute(sql, data)
    conn.commit()

    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)