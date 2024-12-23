from sqlalchemy import create_engine
from pandas import read_sql, DataFrame
from threading import Lock
import pymssql

class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    engine = None
    str_connection: str

    def __init__(self, engine_l: str) -> None:
        self.engine = create_engine(engine_l)
        self.str_connection = engine_l

    def executable_query(self, query: str) -> DataFrame:
        try:
            data = read_sql(query, self.engine)
            return data
        except Exception as e:
            print("strconn:", self.str_connection)
            print("Error al ejecutar consulta:", e)
            self.engine = create_engine(self.str_connection)
            return DataFrame()
            
    def procedure(self, query: str) -> None:
        try:
            connection = self.engine.raw_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            connection.close()
        except Exception as e:
            print("Error al ejecutar el procedimiento almacenado:", e)
                
    def to_sql(self, data: DataFrame, table: str, batch_size: int = None) -> None:
        try:
            with self.engine.begin() as connection:
                # Configura fast_executemany en el cursor subyacente
                raw_conn = connection.connection
                raw_conn.fast_executemany = True
                
                if batch_size:
                    for i in range(0, len(data), batch_size):
                        batch = data.iloc[i:i + batch_size]
                        batch.to_sql(name=table, con=connection, if_exists='append', index=False)
                else:
                    data.to_sql(name=table, con=connection, if_exists='append', index=False)
        except Exception as e:
            print("Error al cargar datos, haciendo rollback:", e)
            self.engine = create_engine(self.str_connection)  # Reinicia la conexión si es necesario
