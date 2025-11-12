"""
Módulo para el diseño y visualización de bolsas
"""
from modules.color_manager import ColorManager

class BagDesigner:
    """Gestiona el diseño de bolsas según el tipo"""
    
    # Tipos de modelo
    SIMPLE = "simple"
    COMBINADO = "combinado"
    ESPECIAL = "especial"
    
    def __init__(self, tipo_modelo, ancho=300, alto=400):
        self.tipo = tipo_modelo
        self.ancho = ancho
        self.alto = alto
        self.elementos = []  # Para modelo especial
    
    def create_simple_design(self, color_principal, color_asa=None):
        """
        Crea diseño simple: un solo color + asas blancas o negras
        """
        if color_asa is None:
            color_asa = ColorManager.suggest_handle_color([color_principal])
        
        design = {
            'tipo': self.SIMPLE,
            'ancho': self.ancho,
            'alto': self.alto,
            'elementos': [
                {
                    'tipo': 'rectangulo',
                    'x': 0,
                    'y': 0,
                    'ancho': self.ancho,
                    'alto': self.alto,
                    'color': color_principal,
                    'nombre': 'cuerpo'
                },
                {
                    'tipo': 'asa',
                    'x1': self.ancho * 0.25,
                    'y1': 0,
                    'x2': self.ancho * 0.35,
                    'y2': -30,
                    'ancho_linea': 10,
                    'color': color_asa,
                    'nombre': 'asa_izquierda'
                },
                {
                    'tipo': 'asa',
                    'x1': self.ancho * 0.65,
                    'y1': 0,
                    'x2': self.ancho * 0.75,
                    'y2': -30,
                    'ancho_linea': 10,
                    'color': color_asa,
                    'nombre': 'asa_derecha'
                }
            ],
            'colores_usados': {
                'principal': color_principal,
                'asa': color_asa
            }
        }
        
        return design
    
    def create_combinado_design(self, color_principal, color_secundario, color_asa=None):
        """
        Crea diseño combinado: 1/4 de un color, resto de otro
        """
        if color_asa is None:
            color_asa = ColorManager.suggest_handle_color([color_principal, color_secundario])
        
        cuarto = self.alto * 0.25
        
        design = {
            'tipo': self.COMBINADO,
            'ancho': self.ancho,
            'alto': self.alto,
            'elementos': [
                {
                    'tipo': 'rectangulo',
                    'x': 0,
                    'y': 0,
                    'ancho': self.ancho,
                    'alto': cuarto,
                    'color': color_secundario,
                    'nombre': 'superior'
                },
                {
                    'tipo': 'rectangulo',
                    'x': 0,
                    'y': cuarto,
                    'ancho': self.ancho,
                    'alto': self.alto - cuarto,
                    'color': color_principal,
                    'nombre': 'inferior'
                },
                {
                    'tipo': 'asa',
                    'x1': self.ancho * 0.25,
                    'y1': 0,
                    'x2': self.ancho * 0.35,
                    'y2': -30,
                    'ancho_linea': 10,
                    'color': color_asa,
                    'nombre': 'asa_izquierda'
                },
                {
                    'tipo': 'asa',
                    'x1': self.ancho * 0.65,
                    'y1': 0,
                    'x2': self.ancho * 0.75,
                    'y2': -30,
                    'ancho_linea': 10,
                    'color': color_asa,
                    'nombre': 'asa_derecha'
                }
            ],
            'colores_usados': {
                'principal': color_principal,
                'secundario': color_secundario,
                'asa': color_asa
            }
        }
        
        return design
    
    def create_especial_design(self):
        """
        Crea estructura base para diseño especial (personalizable)
        """
        design = {
            'tipo': self.ESPECIAL,
            'ancho': self.ancho,
            'alto': self.alto,
            'elementos': [],
            'colores_usados': {}
        }
        
        return design
    
    def add_element_especial(self, design, elemento):
        """
        Añade un elemento al diseño especial
        elemento: dict con tipo, posición, tamaño y color
        """
        if design['tipo'] != self.ESPECIAL:
            raise ValueError("Solo se pueden añadir elementos a diseños especiales")
        
        # Validar que el elemento esté dentro de los límites
        if elemento.get('x', 0) < 0 or elemento.get('y', 0) < 0:
            raise ValueError("Posición fuera de límites")
        
        if elemento.get('x', 0) + elemento.get('ancho', 0) > self.ancho:
            raise ValueError("Elemento excede ancho de bolsa")
        
        if elemento.get('y', 0) + elemento.get('alto', 0) > self.alto:
            raise ValueError("Elemento excede alto de bolsa")
        
        design['elementos'].append(elemento)
        
        # Registrar color usado
        if 'color' in elemento:
            color_key = f"color_{len(design['elementos'])}"
            design['colores_usados'][color_key] = elemento['color']
        
        return design
    
    def validate_design(self, design, esquema):
        """
        Valida que el diseño cumpla con el esquema de colores
        """
        colores = list(design['colores_usados'].values())
        # Filtrar colores de asa (blanco/negro)
        colores_cuerpo = [c for c in colores if c not in ['#FFFFFF', '#000000', '#ffffff', '#000000']]
        
        if len(colores_cuerpo) < 2:
            return True  # Un solo color siempre es válido
        
        return ColorManager.validate_harmony(colores_cuerpo, esquema)
    
    def get_svg_representation(self, design):
        """
        Genera representación SVG del diseño
        """
        svg_elements = []
        
        # Header SVG
        svg_header = f'<svg width="{design["ancho"]}" height="{design["alto"] + 50}" xmlns="http://www.w3.org/2000/svg">'
        svg_elements.append(svg_header)
        
        # Renderizar elementos
        for elem in design['elementos']:
            if elem['tipo'] == 'rectangulo':
                svg_elements.append(
                    f'<rect x="{elem["x"]}" y="{elem["y"]}" '
                    f'width="{elem["ancho"]}" height="{elem["alto"]}" '
                    f'fill="{elem["color"]}" stroke="#333" stroke-width="1"/>'
                )
            elif elem['tipo'] == 'asa':
                # Dibujar asa como línea curva
                svg_elements.append(
                    f'<path d="M {elem["x1"]},{elem["y1"]} '
                    f'Q {(elem["x1"] + elem["x2"]) / 2},{elem["y2"]} '
                    f'{elem["x2"]},{elem["y1"]}" '
                    f'stroke="{elem["color"]}" stroke-width="{elem["ancho_linea"]}" '
                    f'fill="none" stroke-linecap="round"/>'
                )
        
        svg_elements.append('</svg>')
        
        return '\n'.join(svg_elements)
    
    @staticmethod
    def get_available_models():
        """Retorna los modelos disponibles"""
        return [
            {
                'id': BagDesigner.SIMPLE,
                'nombre': 'Simple',
                'descripcion': 'Un solo color + asas (blanco o negro)',
                'colores_requeridos': 1
            },
            {
                'id': BagDesigner.COMBINADO,
                'nombre': 'Combinado',
                'descripcion': '1/4 superior de un color, resto de otro',
                'colores_requeridos': 2
            },
            {
                'id': BagDesigner.ESPECIAL,
                'nombre': 'Especial',
                'descripcion': 'Diseño personalizado con herramientas',
                'colores_requeridos': 'variable'
            }
        ]