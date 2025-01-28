
---

# Mssql Facade

## Instalación

```bash
pip3 install mssqldbfacade
```

## Manual de uso
1. **Variables de Entorno**

| Variable | Tipo de dato |
|:-|-:|
|MSSQL_STRING_CONNECTION|string|

2. **Funciones**:
   - **`get_data(query)`**: Este método permite ejecutar una consulta SQL y obtener los resultados como un DataFrame de pandas.
   - **`update_data(name, data)`**: Este método ejecuta un procedimiento almacenado en la base de datos, enviando un DataFrame como parámetro.
   - **`modify_data(query, data)`**: Este método utiliza el paquete pandasql para aplicar una consulta SQL a un DataFrame local.

3. **Ejemplos de Uso**
```py
from mssql_database_facade import DatabaseFacade
import pandas as pd

# Crear instancia de la fachada
db_facade = DatabaseFacade()

# Consultar datos
query = "SELECT * FROM mi_tabla"
data = db_facade.get_data(query)
print(data)

# Modificar datos utilizando pandasql
modify_query = "SELECT * FROM data WHERE columna > 10"
modified_data = db_facade.modify_data(modify_query, data)
print(modified_data)

# Actualizar datos con un procedimiento almacenado
update_data = pd.DataFrame([{"columna1": "valor1", "columna2": "valor2"}])
db_facade.update_data("mi_procedimiento", update_data)

```

---

By: Alan Medina ⚙️
