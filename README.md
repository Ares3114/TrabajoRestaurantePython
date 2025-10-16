
# Sistema de Fidelización (Python / POO / Consola)

**Objetivo**: Clasificar clientes (Regular, VIP, Super VIP) según número de visitas en una ventana móvil (por defecto 3 meses), usando programación orientada a objetos y patrones (Strategy, Singleton, Repository).

## Estructura
- `models.py`: Entidades y reglas.
- `repositories.py`: Lectura CSV y utilidades de visitas.
- `strategies.py`: Estrategias de clasificación (por visitas en ventana).
- `engine.py`: Motor de fidelización.
- `report.py`: Reportes (visitas por mes, ranking).
- `config.py`: Singleton con reglas por defecto (editable en menú).
- `main.py`: Menú de consola.
- `sample_data/reservas.csv`: Datos de ejemplo.
- `tests/test_logic.py`: Pruebas unitarias básicas.

## Requisitos
- Python 3.10+ (sin dependencias externas).

## Uso
```bash
cd resto_loyalty_python
python main.py
# Ruta por defecto del CSV: sample_data/reservas.csv
```

## Menú principal
1. Importar reservas (CSV)  
2. Configurar reglas de fidelización  
3. Buscar cliente por ID y ver categoría actual  
4. Listar clientes por categoría  
5. Reporte: visitas por mes (últimos N)  
6. Ranking top clientes (últimos N meses)  
7. Exportar ranking a CSV  
0. Salir

## CSV esperado
Columnas: `reservation_id,customer_id,name,email,phone,datetime,party_size`  
Fechas permitidas: `YYYY-MM-DDTHH:MM`, `YYYY-MM-DD HH:MM` o solo `YYYY-MM-DD`.

## Pruebas
```bash
python -m unittest tests/test_logic.py -v
```
