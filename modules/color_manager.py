"""
Módulo para gestión de colores y paletas
"""
import colorsys
import math

class ColorManager:
    """Gestiona la teoría del color y validaciones"""
    
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convierte color hexadecimal a RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb):
        """Convierte RGB a hexadecimal"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    
    @staticmethod
    def rgb_to_hsv(rgb):
        """Convierte RGB (0-255) a HSV (0-360, 0-100, 0-100)"""
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return (h * 360, s * 100, v * 100)
    
    @staticmethod
    def hsv_to_rgb(hsv):
        """Convierte HSV (0-360, 0-100, 0-100) a RGB (0-255)"""
        h, s, v = hsv[0] / 360.0, hsv[1] / 100.0, hsv[2] / 100.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @staticmethod
    def get_complementary(hex_color):
        """Obtiene el color complementario"""
        rgb = ColorManager.hex_to_rgb(hex_color)
        hsv = ColorManager.rgb_to_hsv(rgb)
        # Complementario: +180 grados en el círculo cromático
        comp_h = (hsv[0] + 180) % 360
        comp_rgb = ColorManager.hsv_to_rgb((comp_h, hsv[1], hsv[2]))
        return ColorManager.rgb_to_hex(comp_rgb)
    
    @staticmethod
    def get_analogous(hex_color, angle=30):
        """Obtiene colores análogos (±30 grados por defecto)"""
        rgb = ColorManager.hex_to_rgb(hex_color)
        hsv = ColorManager.rgb_to_hsv(rgb)
        
        analogous_colors = []
        for offset in [-angle, angle]:
            new_h = (hsv[0] + offset) % 360
            new_rgb = ColorManager.hsv_to_rgb((new_h, hsv[1], hsv[2]))
            analogous_colors.append(ColorManager.rgb_to_hex(new_rgb))
        
        return analogous_colors
    
    @staticmethod
    def get_triadic(hex_color):
        """Obtiene colores triádicos (120 grados de separación)"""
        rgb = ColorManager.hex_to_rgb(hex_color)
        hsv = ColorManager.rgb_to_hsv(rgb)
        
        triadic_colors = []
        for offset in [120, 240]:
            new_h = (hsv[0] + offset) % 360
            new_rgb = ColorManager.hsv_to_rgb((new_h, hsv[1], hsv[2]))
            triadic_colors.append(ColorManager.rgb_to_hex(new_rgb))
        
        return triadic_colors
    
    @staticmethod
    def validate_harmony(colors, scheme):
        """
        Valida si una combinación de colores cumple con el esquema
        colors: lista de colores en hex
        scheme: 'armonico', 'complementario', 'analogo'
        """
        if len(colors) < 2:
            return True
        
        # Convertir a HSV para análisis
        hsv_colors = [ColorManager.rgb_to_hsv(ColorManager.hex_to_rgb(c)) for c in colors]
        
        if scheme == 'complementario':
            # Los colores deben estar aproximadamente opuestos (±30 grados)
            h1, h2 = hsv_colors[0][0], hsv_colors[1][0]
            diff = abs(h1 - h2)
            # Normalizar la diferencia
            if diff > 180:
                diff = 360 - diff
            return 150 <= diff <= 210
        
        elif scheme == 'analogo':
            # Los colores deben estar cercanos (máximo 60 grados)
            for i in range(len(hsv_colors) - 1):
                h1, h2 = hsv_colors[i][0], hsv_colors[i + 1][0]
                diff = abs(h1 - h2)
                if diff > 180:
                    diff = 360 - diff
                if diff > 60:
                    return False
            return True
        
        elif scheme == 'armonico':
            # Los colores pueden ser análogos, triádicos o complementarios
            # Más flexible, solo verificar que no sean idénticos
            for i in range(len(hsv_colors) - 1):
                h1, h2 = hsv_colors[i][0], hsv_colors[i + 1][0]
                diff = abs(h1 - h2)
                if diff > 180:
                    diff = 360 - diff
                if diff < 10:  # Demasiado similares
                    return False
            return True
        
        return True
    
    @staticmethod
    def get_contrast_ratio(hex1, hex2):
        """Calcula el ratio de contraste entre dos colores"""
        def get_luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        rgb1 = ColorManager.hex_to_rgb(hex1)
        rgb2 = ColorManager.hex_to_rgb(hex2)
        
        lum1 = get_luminance(rgb1)
        lum2 = get_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def suggest_handle_color(body_colors):
        """
        Sugiere colores para las asas (blanco o negro) según el cuerpo de la bolsa
        """
        white = "#FFFFFF"
        black = "#000000"
        
        # Calcular contraste promedio con blanco y negro
        white_contrast = sum(ColorManager.get_contrast_ratio(c, white) for c in body_colors) / len(body_colors)
        black_contrast = sum(ColorManager.get_contrast_ratio(c, black) for c in body_colors) / len(body_colors)
        
        # Retornar el que tenga mejor contraste
        return white if white_contrast > black_contrast else black