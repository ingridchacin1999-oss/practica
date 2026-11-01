import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            clave TEXT
        )
    ''')
    # Tabla de facturas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_factura TEXT,
            cliente TEXT,
            monto REAL,
            fecha TEXT
        )
    ''')
    
    # Insertar datos de prueba si están vacías
    cursor.execute("SELECT count(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (usuario, clave) VALUES ('admin', 'admin123')")
        cursor.execute("INSERT INTO usuarios (usuario, clave) VALUES ('user1', 'clave123')")
        
    cursor.execute("SELECT count(*) FROM facturas")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO facturas (numero_factura, cliente, monto, fecha) VALUES ('FAC-001', 'Empresa A', 150.50, '2026-01-15')")
        cursor.execute("INSERT INTO facturas (numero_factura, cliente, monto, fecha) VALUES ('FAC-002', 'Empresa B', 1200.00, '2026-01-20')")
        cursor.execute("INSERT INTO facturas (numero_factura, cliente, monto, fecha) VALUES ('FAC-003', 'Cliente Juan', 85.00, '2026-02-01')")
        
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return '''
        <h2>Sistema de Pruebas de Seguridad e Información</h2>
        <ul>
            <li><a href="/login-vulnerable">Login Vulnerable (SQLi)</a></li>
            <li><a href="/login-seguro">Login Seguro</a></li>
            <li><a href="/facturas">Módulo de Facturas</a></li>
        </ul>
    '''

@app.route('/login-vulnerable', methods=['GET', 'POST'])
def login_vulnerable():
    msg = ''
    if request.method == 'POST':
        user = request.form.get('usuario', '')
        clave = request.form.get('clave', '')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # Vulnerable a SQL Injection por concatenación
        query = f"SELECT * FROM usuarios WHERE usuario = '{user}' AND clave = '{clave}'"
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                msg = f'<h3 style="color:green;">¡Acceso concedido! Bienvenido, {result[1]}.</h3>'
            else:
                msg = '<h3 style="color:red;">Credenciales incorrectas.</h3>'
        except Exception as e:
            msg = f'<h3 style="color:red;">Error SQL: {e}</h3>'
        conn.close()
    
    return f'''
        <h2>Login Vulnerable</h2>
        <form method="POST">
            Usuario: <input type="text" name="usuario"><br><br>
            Clave: <input type="password" name="clave"><br><br>
            <input type="submit" value="Ingresar">
        </form>
        {msg}
    '''

@app.route('/login-seguro', methods=['GET', 'POST'])
def login_seguro():
    msg = ''
    if request.method == 'POST':
        user = request.form.get('usuario', '')
        clave = request.form.get('clave', '')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # Seguro usando consultas parametrizadas
        query = "SELECT * FROM usuarios WHERE usuario = ? AND clave = ?"
        cursor.execute(query, (user, clave))
        result = cursor.fetchone()
        if result:
            msg = f'<h3 style="color:green;">¡Acceso concedido de forma segura!</h3>'
        else:
            msg = '<h3 style="color:red;">Credenciales incorrectas.</h3>'
        conn.close()
    
    return f'''
        <h2>Login Seguro</h2>
        <form method="POST">
            Usuario: <input type="text" name="usuario"><br><br>
            Clave: <input type="password" name="clave"><br><br>
            <input type="submit" value="Ingresar">
        </form>
        {msg}
    '''

@app.route('/facturas')
def ver_facturas():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM facturas")
    rows = cursor.fetchall()
    conn.close()
    
    html = '''
        <h2>Lista de Facturas Registradas</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>ID</th>
                <th>N° Factura</th>
                <th>Cliente</th>
                <th>Monto ($)</th>
                <th>Fecha</th>
            </tr>
    '''
    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
    html += '</table><br><a href="/">Volver al inicio</a>'
    return html

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)