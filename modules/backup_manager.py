"""
Módulo para gestión de respaldos de base de datos
"""
import os
import shutil
from datetime import datetime

class BackupManager:
    """Gestiona respaldos de la base de datos"""
    
    @staticmethod
    def crear_respaldo():
        """
        Crea un respaldo de la base de datos
        """
        try:
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"respaldo_chromabags_{fecha}.db"
            
            # Buscar la base de datos
            posibles_rutas = [
                "database/ChromaBags.db",
                "instance/chromabags.db",
                "chromabags.db",
                "app.db",
                "database.db"
            ]
            
            ruta_bd_original = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    ruta_bd_original = ruta
                    break
            
            if not ruta_bd_original:
                return {
                    'success': False, 
                    'error': 'No se pudo encontrar la base de datos'
                }
            
            # Crear carpeta de respaldos
            carpeta_respaldos = "respaldos"
            if not os.path.exists(carpeta_respaldos):
                os.makedirs(carpeta_respaldos)
            
            ruta_respaldo = os.path.join(carpeta_respaldos, nombre_archivo)
            shutil.copy2(ruta_bd_original, ruta_respaldo)
            
            # Obtener tamaño del archivo
            tamano = os.path.getsize(ruta_respaldo)
            tamano_mb = tamano / (1024 * 1024)
            
            return {
                'success': True,
                'ruta': ruta_respaldo,
                'nombre': nombre_archivo,
                'tamano_mb': round(tamano_mb, 2)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error al generar el respaldo: {str(e)}"
            }
    
    @staticmethod
    def obtener_respaldos():
        """
        Obtiene lista de respaldos existentes
        """
        try:
            carpeta_respaldos = "respaldos"
            
            if not os.path.exists(carpeta_respaldos):
                return []
            
            respaldos = []
            for archivo in os.listdir(carpeta_respaldos):
                if archivo.endswith('.db'):
                    ruta_completa = os.path.join(carpeta_respaldos, archivo)
                    tamano = os.path.getsize(ruta_completa)
                    fecha_mod = os.path.getmtime(ruta_completa)
                    
                    respaldos.append({
                        'nombre': archivo,
                        'ruta': ruta_completa,
                        'tamano_mb': round(tamano / (1024 * 1024), 2),
                        'fecha': datetime.fromtimestamp(fecha_mod).strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            # Ordenar por fecha (más recientes primero)
            respaldos.sort(key=lambda x: x['fecha'], reverse=True)
            
            return respaldos
        
        except Exception as e:
            print(f"Error obteniendo respaldos: {e}")
            return []
    
    @staticmethod
    def eliminar_respaldo(nombre_archivo):
        """
        Elimina un respaldo específico
        """
        try:
            ruta = os.path.join("respaldos", nombre_archivo)
            
            if os.path.exists(ruta):
                os.remove(ruta)
                return {'success': True}
            else:
                return {'success': False, 'error': 'Archivo no encontrado'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def limpiar_respaldos_antiguos(dias=30):
        """
        Elimina respaldos más antiguos que X días
        """
        try:
            carpeta_respaldos = "respaldos"
            
            if not os.path.exists(carpeta_respaldos):
                return {'success': True, 'eliminados': 0}
            
            fecha_limite = datetime.now().timestamp() - (dias * 24 * 60 * 60)
            eliminados = 0
            
            for archivo in os.listdir(carpeta_respaldos):
                if archivo.endswith('.db'):
                    ruta_completa = os.path.join(carpeta_respaldos, archivo)
                    fecha_mod = os.path.getmtime(ruta_completa)
                    
                    if fecha_mod < fecha_limite:
                        os.remove(ruta_completa)
                        eliminados += 1
            
            return {'success': True, 'eliminados': eliminados}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}