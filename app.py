from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import json
from db_connection import get_connection
from modules.color_manager import ColorManager
from modules.bag_designer import BagDesigner
from modules.inventory_manager import InventoryManager
from modules.quotation_manager import QuotationManager
from modules.orders_manager import OrdersManager
from modules.backup_manager import BackupManager

app = Flask(__name__)

# Página principal
@app.route('/')
def index():
    return redirect(url_for('clientes'))

# ==================== CLIENTES ====================
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

# ==================== CATÁLOGO ====================
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

# ==================== DISEÑO COLOR ====================
@app.route('/diseno_color', methods=['GET', 'POST'])
def diseno_color():
    if request.method == 'POST':
        esquema = request.form['esquema_color']
        id_modelo = request.form['modelo_bolsa']
        nombre = request.form['nombre_combinacion']

        color_principal = request.form.get('color_principal')
        color_secundario = request.form.get('color_secundario')
        color_asa = request.form.get('color_asa')
        elementos_json = request.form.get('elementos_json')

        conn = get_connection()
        if conn:
            cur = conn.cursor()

            def obtener_id_color(hex_code):
                if not hex_code:
                    return None
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
            """, (id_modelo, esquema, id_color_principal, id_color_secundario, 
                  id_color_asa, nombre, elementos_json))
            conn.commit()
            cur.close()
            conn.close()

        return redirect(url_for('catalogo'))

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

    return render_template('diseno_color.html', modelos=modelos, paletas=paletas, 
                         combinaciones=combinaciones)

# ==================== INVENTARIO ====================
@app.route('/inventario')
def inventario():
    inventario_data = InventoryManager.obtener_inventario_completo()
    materiales = InventoryManager.obtener_materiales()
    return render_template('inventario.html', inventario=inventario_data, materiales=materiales)

@app.route('/agregar_material', methods=['POST'])
def agregar_material():
    nombre = request.form['nombre_material']
    tipo = request.form['tipo']
    unidad_medida = request.form['unidad_medida']
    costo_unitario = float(request.form['costo_unitario'])
    descripcion = request.form.get('descripcion')
    
    resultado = InventoryManager.agregar_material(
        nombre, tipo, unidad_medida, costo_unitario, descripcion
    )
    
    if not resultado['success']:
        print(f"Error al agregar material: {resultado['error']}")
    
    return redirect(url_for('inventario'))

@app.route('/actualizar_stock', methods=['POST'])
def actualizar_stock():
    id_material = int(request.form['id_material'])
    cantidad = float(request.form['cantidad'])
    
    resultado = InventoryManager.actualizar_stock(id_material, cantidad)
    
    if not resultado['success']:
        print(f"Error al actualizar stock: {resultado['error']}")
    
    return redirect(url_for('inventario'))

@app.route('/api/verificar_material', methods=['POST'])
def api_verificar_material():
    data = request.json
    id_material = data.get('id_material')
    cantidad = data.get('cantidad')
    
    disponible = InventoryManager.verificar_disponibilidad(id_material, cantidad)
    
    return jsonify({'disponible': disponible})

@app.route('/api/materiales_bajo_stock')
def api_materiales_bajo_stock():
    umbral = request.args.get('umbral', 100, type=int)
    materiales = InventoryManager.obtener_materiales_bajo_stock(umbral)
    return jsonify(materiales)

@app.route('/eliminar_material/<int:id>', methods=['POST'])
def eliminar_material(id):
    resultado = InventoryManager.eliminar_material(id)
    if not resultado['success']:
        print(f"Error al eliminar material: {resultado['error']}")
    return redirect(url_for('inventario'))

# ==================== COTIZACIÓN ====================
@app.route('/cotizacion')
def cotizacion():
    cotizaciones = QuotationManager.obtener_cotizaciones()
    
    conn = get_connection()
    clientes_data = []
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT id_cliente, nombre_cliente FROM clientes ORDER BY nombre_cliente")
        clientes_data = cur.fetchall()
        cur.close()
        conn.close()
    
    productos = QuotationManager.obtener_productos_disponibles()
    
    return render_template('cotizacion.html', 
                         cotizaciones=cotizaciones, 
                         clientes=clientes_data,
                         productos=productos)

@app.route('/generar_cotizacion', methods=['POST'])
def generar_cotizacion():
    id_cliente = int(request.form['id_cliente'])
    
    productos = []
    index = 1
    while f'productos[{index}][id_combinacion]' in request.form:
        id_combinacion = request.form.get(f'productos[{index}][id_combinacion]')
        cantidad = request.form.get(f'productos[{index}][cantidad]')
        
        if id_combinacion and cantidad:
            precio = 180
            
            productos.append({
                'id_combinacion': int(id_combinacion),
                'cantidad': int(cantidad),
                'precio_unitario': precio
            })
        
        index += 1
    
    if not productos:
        return redirect(url_for('cotizacion'))
    
    resultado = QuotationManager.crear_cotizacion(id_cliente, productos)
    
    if not resultado['success']:
        print(f"Error al crear cotización: {resultado['error']}")
    
    return redirect(url_for('cotizacion'))

@app.route('/api/cotizacion/<int:id>')
def api_cotizacion_detalle(id):
    cotizacion = QuotationManager.obtener_cotizacion_detalle(id)
    return jsonify(cotizacion)

@app.route('/api/cotizacion/<int:id>/estado', methods=['PUT'])
def api_actualizar_estado_cotizacion(id):
    data = request.json
    nuevo_estado = data.get('estado')
    
    resultado = QuotationManager.actualizar_estado_cotizacion(id, nuevo_estado)
    return jsonify(resultado)

@app.route('/eliminar_cotizacion/<int:id>', methods=['POST'])
def eliminar_cotizacion(id):
    resultado = QuotationManager.eliminar_cotizacion(id)
    if not resultado['success']:
        print(f"Error al eliminar cotización: {resultado['error']}")
    return redirect(url_for('cotizacion'))

@app.route('/duplicar_cotizacion/<int:id>', methods=['POST'])
def duplicar_cotizacion(id):
    resultado = QuotationManager.duplicar_cotizacion(id)
    if not resultado['success']:
        print(f"Error al duplicar cotización: {resultado['error']}")
    return redirect(url_for('cotizacion'))

@app.route('/api/productos_cotizacion')
def api_productos_cotizacion():
    productos = QuotationManager.obtener_productos_disponibles()
    return jsonify(productos)

# ==================== PEDIDOS ====================
@app.route('/pedidos')
def pedidos():
    conn = get_connection()
    clientes_data = []
    productos_data = []
    
    if conn:
        cur = conn.cursor()
        
        # Clientes
        cur.execute("SELECT id_cliente, nombre_cliente FROM clientes ORDER BY nombre_cliente")
        clientes_data = cur.fetchall()
        
        # Productos desde el catálogo (combinaciones)
        cur.execute("""
            SELECT 
                c.id_combinacion,
                c.nombre_guardado,
                mb.nombre_modelo,
                mb.tipo
            FROM combinaciones c
            JOIN modelos_bolsas mb ON c.id_modelo = mb.id_modelo
            ORDER BY c.nombre_guardado
        """)
        productos_data = cur.fetchall()
        
        cur.close()
        conn.close()
    
    pedidos_data = OrdersManager.obtener_pedidos()
    
    return render_template('pedidos.html',
                         clientes=clientes_data,
                         productos=productos_data,
                         pedidos=pedidos_data)

@app.route('/guardar_pedido', methods=['POST'])
def guardar_pedido():
    id_cliente = request.form['id_cliente']
    id_combinacion = request.form['id_combinacion']  # Ahora es id_combinacion
    cantidad = int(request.form['cantidad'])
    fecha_entrega = request.form['fecha_entrega']
    estado = request.form['estado']
    
    resultado = OrdersManager.crear_pedido(
        id_cliente, id_combinacion, cantidad, fecha_entrega, estado
    )
    
    if not resultado['success']:
        print(f"Error al guardar pedido: {resultado['error']}")
    
    return redirect(url_for('pedidos'))

@app.route('/editar_pedido/<int:id_pedido>', methods=['GET', 'POST'])
def editar_pedido(id_pedido):
    if request.method == 'POST':
        fecha_entrega = request.form['fecha_entrega']
        estado = request.form['estado']
        
        resultado = OrdersManager.actualizar_pedido(id_pedido, fecha_entrega, estado)
        
        if not resultado['success']:
            print(f"Error al actualizar pedido: {resultado['error']}")
        
        return redirect(url_for('pedidos'))
    
    pedido = OrdersManager.obtener_pedido(id_pedido)
    return render_template('editar_pedido.html', pedido=pedido)

@app.route('/eliminar_pedido/<int:id_pedido>')
def eliminar_pedido(id_pedido):
    resultado = OrdersManager.eliminar_pedido(id_pedido)
    
    if not resultado['success']:
        print(f"Error al eliminar pedido: {resultado['error']}")
    
    return redirect(url_for('pedidos'))

# ==================== REPORTES ====================
@app.route('/reportes')
def reportes():
    datos = OrdersManager.obtener_pedidos_por_estado()
    estadisticas = OrdersManager.obtener_estadisticas_dashboard()
    
    # Valores por defecto si no hay estadísticas
    if not estadisticas:
        estadisticas = {
            'total_pedidos': 0,
            'por_estado': {},
            'ingresos_totales': 0,
            'pedidos_mes': 0,
            'ingresos_mes': 0,
            'clientes_activos': 0,
            'productos_top': [],
            'ventas_mensuales': []
        }
    
    return render_template('reportes.html',
                         por_entregar=datos['por_entregar'],
                         entregados=datos['entregados'],
                         vencidos=datos['vencidos'],
                         todos=datos['todos'],
                         estadisticas=estadisticas)

# ==================== RESPALDO ====================
@app.route('/respaldo')
def respaldo():
    respaldos = BackupManager.obtener_respaldos()
    return render_template('respaldo.html', respaldos=respaldos)

@app.route('/descargar_respaldo')
def descargar_respaldo():
    resultado = BackupManager.crear_respaldo()
    
    if not resultado['success']:
        return resultado['error'], 500
    
    return send_file(
        resultado['ruta'],
        as_attachment=True,
        download_name=resultado['nombre']
    )

# ==================== APIs DE COLOR Y DISEÑO ====================
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
        
        else:
            return jsonify({'error': 'Tipo de modelo no válido'}), 400
        
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

# ==================== OTRAS RUTAS ====================
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
        
        if combinacion:
            color_ids = [
                combinacion[3],
                combinacion[4],
                combinacion[5],
                combinacion[6]
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

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5050)