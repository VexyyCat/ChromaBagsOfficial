# 🎨 ChromaBags - Sistema Integral de Gestión

<div align="center">

![ChromaBags Logo](static/images/logo_chromabags.png)

**Sistema completo de gestión empresarial para confeccionistas de bolsas**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

[Características](#características) •
[Instalación](#instalación) •
[Uso](#uso) •
[Módulos](#módulos) •
[Capturas](#capturas) •
[Contribuir](#contribuir)

</div>

---

## Descripción

**ChromaBags** es un sistema integral de gestión empresarial diseñado específicamente para pequeñas y medianas empresas dedicadas a la confección de bolsas personalizadas. Desarrollado con Flask y tecnologías web modernas, ofrece una solución completa desde el diseño hasta la facturación.

### Problema que Resuelve

Los confeccionistas de bolsas enfrentan desafíos diarios en:
- Gestión manual de inventarios
- Cálculos de costos complejos
- Seguimiento de pedidos
- Facturación y reportes

**ChromaBags** digitaliza y automatiza estos procesos, permitiendo a los empresarios enfocarse en lo que mejor hacen: crear productos de calidad.

---

## Características

### Diseño y Catálogo
- **Editor visual de diseños** con teoría del color aplicada
- **Catálogo digital** de productos con visualización SVG
- **Esquemas de armonía cromática** (complementarios, análogos, triádicos)
- **Modelos de bolsas**: Simple, Combinado y Especial

### Gestión de Clientes
- Base de datos completa de clientes
- Datos fiscales para facturación electrónica
- Historial de compras por cliente
- Segmentación por tipo (Primerizo, Frecuente, Ocasional)

### Inventario Inteligente
- Control de stock en tiempo real
- Alertas de materiales bajo stock
- Cálculo automático de costos
- Exportación a Excel

### Cotizaciones
- Generación rápida de cotizaciones
- Múltiples productos por cotización
- Cálculo automático con IVA
- Estados: Pendiente, Aprobada, Rechazada
- Conversión automática a pedidos

### Gestión de Pedidos
- Seguimiento completo del ciclo de vida
- Estados: Pendiente → En Proceso → Finalizado → Entregado
- Detección automática de pedidos vencidos
- Actualización rápida desde tabla

### Pagos y Facturación
- Registro de pagos con múltiples métodos
- Generación de facturas PDF con datos fiscales
- Cumplimiento con requisitos del SAT (México)
- Desglose de IVA (16%)

### Reportes y Analytics
- Dashboard con KPIs principales
- Gráficas de ventas mensuales
- Productos más vendidos
- Análisis de pedidos por estado
- Exportación de reportes

### Respaldo y Seguridad
- Sistema de respaldos automáticos
- Base de datos SQLite embebida
- Exportación de datos

---

## Instalación

### Requisitos Previos

- **Python 3.8 o superior** ([Descargar](https://www.python.org/downloads/))
- **Git** (opcional, para clonar el repositorio)

### Instalación Rápida (Windows)
```bash
