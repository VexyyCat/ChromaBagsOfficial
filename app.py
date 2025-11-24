from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from db_connection import get_connection
from modules.color_manager import ColorManager
from modules.bag_designer import BagDesigner

app = Flask(__name__)

# Página principal
@app.route('/')
def index():
    return redirect(url_for('clientes'))

# Mostrar clientes
@app.route('/clientes')
def clientes():
    conn = get_connection()
    clientes_data = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre_cliente, telefono, correo, tipo_cliente, direccion, id_cliente 
            FROM clientes 
            ORDER BY id_cliente;
        """)
        clientes_data = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('clientes.html', clientes=clientes_data)

# Agregar cliente
@app.route('/agregar_cliente', methods=['POST'])
def agregar_cliente():
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    tipo = request.form['tipo']
    direccion = request.form['direccion']

    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nombre_cliente, telefono, correo, tipo_cliente, direccion)
            VALUES (?, ?, ?, ?, ?);
        """, (nombre, telefono, correo, tipo, direccion))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('clientes'))

# Eliminar cliente
@app.route('/eliminar_cliente/<int:id>', methods=['GET', 'POST'])
def eliminar_cliente(id):
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM clientes WHERE id_cliente = ?;", (id,))
            conn.commit()
        except Exception as e:
            print(f"Error al eliminar cliente: {e}")
        cur.close()
        conn.close()
    return redirect(url_for('clientes'))


# Modificar cliente
@app.route('/modificar_cliente/<int:id>', methods=['POST'])
def modificar_cliente(id):
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    tipo = request.form['tipo']
    direccion = request.form['direccion']

    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE clientes 
            SET nombre_cliente=?, telefono=?, correo=?, tipo_cliente=?, direccion=?
            WHERE id_cliente=?;
        """, (nombre, telefono, correo, tipo, direccion, id))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('clientes'))

# CATALOGO - Solo muestra combinaciones guardadas
@app.route('/catalogo')
def catalogo():
    conn = get_connection()
    combinaciones = []
    if conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                c.id_combinacion,
                c.nombre_guardado,
                c.esquema,
                c.fecha_creacion,
                mb.nombre_modelo,
                mb.tipo,
                cp.codigo_hex AS hex_principal,
                ca.codigo_hex AS hex_asa,
                cs.codigo_hex AS hex_secundario
            FROM combinaciones c
            JOIN modelos_bolsas mb ON c.id_modelo = mb.id_modelo
            LEFT JOIN colores cp ON c.id_color_principal = cp.id_color
            LEFT JOIN colores ca ON c.id_color_asa = ca.id_color
            LEFT JOIN colores cs ON c.id_color_secundario = cs.id_color
            ORDER BY c.fecha_creacion DESC;
        """)
        combinaciones = cur.fetchall()
        cur.close()
        conn.close()
    return render_template('catalogo.html', combinaciones=combinaciones)

# DISEÑO COLOR
@app.route('/diseno_color', methods=['GET', 'POST'])
def diseno_color():
    if request.method == 'POST':
        esquema = request.form['esquema_color']
        id_modelo = request.form['modelo_bolsa']
        nombre = request.form['nombre_combinacion']

        color_principal = request.form.get('color_principal')
        color_secundario = request.form.get('color_secundario')
        color_asa = request.form.get('color_asa')
        diseno_json = request.form.get('diseno_json')

        conn = get_connection()
        if conn:
            cur = conn.cursor()

            def obtener_id_color(hex_code):
                if not hex_code:
                    return None
                # insertar con IGNORE evita duplicados, timeout previene bloqueo
                cur.execute("""
                    INSERT OR IGNORE INTO colores (nombre_color, codigo_hex)
                    VALUES (?, ?)
                """, (f"Color_{hex_code}", hex_code))
                conn.commit()
                cur.execute("SELECT id_color FROM colores WHERE codigo_hex = ?", (hex_code,))
                result = cur.fetchone()
                return result[0] if result else None

            id_color_principal = obtener_id_color(color_principal)
            id_color_secundario = obtener_id_color(color_secundario)
            id_color_asa = obtener_id_color(color_asa)

            cur.execute("""
                INSERT INTO combinaciones (
                    id_modelo, esquema, id_color_principal, 
                    id_color_secundario, id_color_asa, nombre_guardado, diseno_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_modelo, esquema, id_color_principal, id_color_secundario, id_color_asa, nombre, diseno_json))
            conn.commit()
            cur.close()
            conn.close()

        return redirect(url_for('catalogo'))

    # Si no es POST → cargar datos normalmente
    conn = get_connection()
    modelos, paletas, combinaciones = [], [], []
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT id_modelo, nombre_modelo, tipo FROM modelos_bolsas ORDER BY id_modelo;")
        modelos = cur.fetchall()
        cur.execute("SELECT id_paleta, nombre, esquema FROM paletas_colores ORDER BY id_paleta;")
        paletas = cur.fetchall()
        cur.execute("""
            SELECT c.id_combinacion, c.nombre_guardado, c.esquema, c.fecha_creacion,
                   mb.nombre_modelo, mb.tipo
            FROM combinaciones c
            JOIN modelos_bolsas mb ON c.id_modelo = mb.id_modelo
            ORDER BY c.fecha_creacion DESC;
        """)
        combinaciones = cur.fetchall()
        cur.close()
        conn.close()

    return render_template('diseno_color.html', modelos=modelos, paletas=paletas, combinaciones=combinaciones)


# API: Cargar colores según paleta
@app.route('/api/colores_paleta/<int:id_paleta>')
def api_colores_paleta(id_paleta):
    conn = get_connection()
    colores = []
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT nombre_color, codigo_hex FROM colores WHERE id_paleta = ?;", (id_paleta,))
        colores = [{'nombre': row[0], 'hex': row[1]} for row in cur.fetchall()]
        cur.close()
        conn.close()
    return jsonify(colores)

# API: Generar diseño de bolsa
@app.route('/api/generar_diseno', methods=['POST'])
def api_generar_diseno():
    data = request.json
    tipo_modelo = data.get('tipo_modelo')
    esquema = data.get('esquema')
    colores = data.get('colores', [])
    
    try:
        designer = BagDesigner(tipo_modelo)
        
        if tipo_modelo == 'simple':
            if len(colores) < 1:
                return jsonify({'error': 'Se requiere al menos 1 color'}), 400
            design = designer.create_simple_design(colores[0])
        
        elif tipo_modelo == 'combinado':
            if len(colores) < 2:
                return jsonify({'error': 'Se requieren 2 colores'}), 400
            design = designer.create_combinado_design(colores[0], colores[1])
        
        elif tipo_modelo == 'especial':
            design = designer.create_especial_design()
            # Los elementos se añadirán desde el frontend
        
        else:
            return jsonify({'error': 'Tipo de modelo no válido'}), 400
        
        # Validar esquema de colores
        if not designer.validate_design(design, esquema):
            return jsonify({
                'warning': 'Los colores seleccionados no cumplen con el esquema de armonía',
                'design': design
            })
        
        return jsonify({
            'success': True,
            'design': design,
            'svg': designer.get_svg_representation(design)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Validar armonía de colores
@app.route('/api/validar_armonia', methods=['POST'])
def api_validar_armonia():
    data = request.json
    colores = data.get('colores', [])
    esquema = data.get('esquema', 'armonico')
    
    try:
        es_valido = ColorManager.validate_harmony(colores, esquema)
        
        sugerencias = []
        if not es_valido:
            if esquema == 'complementario' and len(colores) >= 1:
                sugerencias.append({
                    'tipo': 'complementario',
                    'color': ColorManager.get_complementary(colores[0])
                })
            elif esquema == 'analogo' and len(colores) >= 1:
                sugerencias.extend([
                    {'tipo': 'analogo', 'color': c}
                    for c in ColorManager.get_analogous(colores[0])
                ])
        
        return jsonify({
            'valido': es_valido,
            'esquema': esquema,
            'sugerencias': sugerencias
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Sugerir color de asa
@app.route('/api/sugerir_asa', methods=['POST'])
def api_sugerir_asa():
    data = request.json
    colores_cuerpo = data.get('colores', [])
    
    try:
        color_sugerido = ColorManager.suggest_handle_color(colores_cuerpo)
        return jsonify({
            'color_sugerido': color_sugerido,
            'nombre': 'Blanco' if color_sugerido == '#FFFFFF' else 'Negro'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ver detalle de combinación
@app.route('/ver_combinacion/<int:id>')
def ver_combinacion(id):
    conn = get_connection()
    combinacion = None
    colores = []
    
    if conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.*, mb.nombre_modelo, mb.tipo
            FROM combinaciones c
            JOIN modelos_bolsas mb ON c.id_modelo = mb.id_modelo
            WHERE c.id_combinacion = ?
        """, (id,))
        combinacion = cur.fetchone()
        
        # Obtener colores asociados
        if combinacion:
            color_ids = [
                combinacion[3],  # id_color_principal
                combinacion[4],  # id_color_secundario
                combinacion[5],  # id_color_hilo
                combinacion[6]   # id_color_asa
            ]
            
            for cid in color_ids:
                if cid:
                    cur.execute("SELECT nombre_color, codigo_hex FROM colores WHERE id_color = ?", (cid,))
                    color = cur.fetchone()
                    if color:
                        colores.append(color)
        
        cur.close()
        conn.close()
    
    return render_template('ver_combinacion.html', combinacion=combinacion, colores=colores)

# Crear producto desde combinación
@app.route('/crear_producto_desde_combinacion', methods=['POST'])
def crear_producto_desde_combinacion():
    data = request.json
    id_combinacion = data.get('id_combinacion')
    nombre_producto = data.get('nombre_producto')
    precio_sugerido = data.get('precio_sugerido')
    stock = data.get('stock', 0)
    
    if not id_combinacion or not nombre_producto:
        return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Error de conexión a BD'}), 500
    
    try:
        cur = conn.cursor()
        
        # Obtener id_modelo de la combinación
        cur.execute("SELECT id_modelo FROM combinaciones WHERE id_combinacion = ?", (id_combinacion,))
        resultado = cur.fetchone()
        
        if not resultado:
            return jsonify({'success': False, 'error': 'Combinación no encontrada'}), 404
        
        id_modelo = resultado[0]
        
        # Insertar producto
        cur.execute("""
            INSERT INTO productos_terminados (
                id_modelo, id_combinacion, nombre_producto, 
                precio_sugerido, stock
            ) VALUES (?, ?, ?, ?, ?)
        """, (id_modelo, id_combinacion, nombre_producto, precio_sugerido, stock))
        
        conn.commit()
        id_producto = cur.lastrowid
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'id_producto': id_producto})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/inventario')
def inventario():
    return render_template('inventario.html')

# 🔹 Ruta para Cotización
@app.route('/cotizacion')
def cotizacion():
    return render_template('cotizacion.html')


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5050)