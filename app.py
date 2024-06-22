from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, json
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key='llave secreta'


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/signup')
def showSignUp():
    return render_template('signup.html')

@app.route('/signin')
def showSignin():
    return render_template('signin.html')

# crear usuario
@app.route('/api/signup', methods=['POST'])
def signUp():
    cursor = None
    conexion = None
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        if _name and _email and _password:
            
            conexion = mysql.connector.connect(
                host ='localhost',
                user ='root',
                passwd ='',
                database ='stocklist'
            )
            if conexion.is_connected():
                cursor = conexion.cursor()
                _hashed_password = generate_password_hash(_password)
                cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
                data = cursor.fetchall()

                if len(data) == 0:
                    conexion.commit()
                    return json.dumps({'message': 'User created successfully!'})
                    print('Datos almacenados correctamente')
                else:
                    return json.dumps({'error': str(data[0])})
                    print('Error al almacenar los datos')
            else:
                return json.dumps({'html': '<span>LLenar todos los campos obligatorios</span>'})
                print('Error al almacenar')
    except Error as e:
        return json.dumps({'error': str(e)})
        print('Error en la conexion o en la consulta: ', e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
            print('Conexion cerrada')
    return redirect('/index')

# iniciar sesion valida
@app.route('/api/validateLogin', methods=['POST'])
def validateLogin():
    _username = request.form.get('inputEmail')
    _password = request.form.get('inputPassword')
    
    if not _username or not _password:
        return render_template('error.html', error='Correo y constraseña son requeridos')

    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='',
            database='stocklist'
        )

        if conexion.is_connected():
            print('Conexion establecida correctamente')
            cursor = conexion.cursor()
            cursor.callproc('sp_validateLogin', (_username, _password))
            data = cursor.fetchall()
            print('Data:', data)
        
            

@app.route('/userhome')
def userHome():
    if session.get('user'):
        return render_template('userhome.html')
    else:
        return render_template('error.html', error='Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
