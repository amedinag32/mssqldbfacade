from pandas import DataFrame
from .singleton import Singleton
from pandasql import sqldf
from os import getenv
from typing import Dict

class DatabaseFacade:
    """
        Fachada de base de datos, crea conexion con un singleton a mssql
    """
    def __init__(self, connection_string: str = getenv("MSSQL_STRING_CONNECTION")):
        self.db = Singleton(connection_string)
        
    def connect(self, connection_string: str = getenv("MSSQL_STRING_CONNECTION")):
        self.db = Singleton(connection_string)

    def get_data(self, query) -> DataFrame:
        """
            Obtiene el resulado de una consulta de base de datos.
        """       
        return self.db.executable_query(query)

    def update_data(self, name, data: DataFrame) -> None:
        """
            Ejecuta un procedimiento almacenado en base de datos, 
            con el nombre y data que se le manden.
        """
        self.db.procedure(f"""
            EXEC {name} '{data.to_json(orient="records")}';
        """)
 
    def to_sql(self, data: DataFrame, table: str) -> None:
        try:
            with self.db.engine.begin() as connection:
                data.to_sql(
                    name=table,
                    con=connection,
                    if_exists='append',
                    chunksize=1000,  # Inserciones en lotes
                    method='multi',   # Inserciones múltiples en una sola consulta
                    index=False
                )
        except Exception as e:
            print("Error al cargar datos: ", e)
            self.connect()
            
    def transaction(self, query) -> None:
        self.db.procedure(query)
        
    def modify_data(self, query: str, data: DataFrame) -> DataFrame:
        """
            Utiliza el paquete sqldf de pandasql para
            filtrar un Dataframe con consultas sql
        """
        return sqldf(query, locals())
       
    def modify_n_data(self, query: str, data: Dict[str, DataFrame]) -> DataFrame:
        """
            Utiliza el paquete sqldf de pandasql para
            filtrar n DataFrames Dataframe con 
            consultas sql
        """
        for var_name, dataframe in data.items():
        # Crear una instrucción de asignación de la forma 'var_name = dataframe'
            exec(f"{var_name} = dataframe")
            
        return sqldf(query, locals())

    def merge(self, table: str, values: dict, unique_columns: list):
        columns = ", ".join(values.keys())
        values_str = ", ".join(
            f"'{v}'" if ("SELECT" not in str(v).upper() and "NULL" not in str(v).upper()) else str(v)
            for v in values.values()
        )
        update_str = ", ".join(f"{k} = source.{k}" for k in values.keys())
        
        # Crear la condición ON con múltiples columnas
        on_condition = " AND ".join(f"target.{col} = source.{col}" for col in unique_columns)
        
        query = f'''
            MERGE INTO {table} AS target
            USING (VALUES ({values_str})) AS source ({columns})
            ON {on_condition}
            WHEN NOT MATCHED THEN
                INSERT ({columns}) VALUES ({values_str})
            WHEN MATCHED THEN
                UPDATE SET {update_str};
        '''
        # print(query)
        self.transaction(query)
        # print("ok")