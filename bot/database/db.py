import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        """Crea una conexión a la base de datos SQLite."""
        try:
            # si no existe la base de datos, la crea
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
            # ejecutamos una consulta
            self.cursor = self.connection.cursor()
            print(f"Conexión a la base de datos SQLite establecida en {self.db_name}")
            # logger.debug(f"Conexión a la base de datos SQLite establecida en {self.db_name}")
        except sqlite3.IntegrityError as integrity_error:
            print(f"Error de integridad: {integrity_error}")
            self.connection.rollback()
            exit()

        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos SQLite: {e}")
            if self.connection:
                self.connection.close()

        # finally:
        #     # Cerrar la conexión
        #     if connection:
        #         connection.close()

    def active_sqlite3_row(self):
        """Activar el modo de fila de SQLite3."""
        self.cursor.row_factory = sqlite3.Row

    def inactive_sqlite3_row(self):
        """Desactivar el modo de fila de SQLite3."""
        self.cursor.row_factory = None

    def get_cursor(self):
        """Obtiene el cursor de la base de datos SQLite."""
        return self.cursor

    def close(self):
        """Cierra la conexión a la base de datos SQLite."""
        if self.connection:
            self.connection.close()  # cerrar la conexion a la base de datos
            print("Conexión a la base de datos SQLite cerrada")
            # logger.debug("Conexión a la base de datos SQLite cerrada")

    def exe_script(self, script: str) -> None:
        """Ejecuta un script en la base de datos SQLite."""
        try:
            if not self.connection:
                self.connect()
            self.cursor.executescript(script)
            self.connection.commit()  # guardar cambios
            # print(f"Script ejecutado: {script}")
            # logger.debug(f"Script ejecutado: {script}")

        except sqlite3.Error as e:
            print(f"Error al ejecutar el script: {e}")
            # logger.error(f"Error al ejecutar el script: {e}")

    # def exe(self, query: str, params=None):
    #     try:
    #         if not self.connection:
    #             self.connect()

    #         if params is not None:
    #             self.cursor.execute(query, params)
    #         else:
    #             self.cursor.execute(query)

    #         # Las consultas de lectura devuelven sus filas.
    #         if self.cursor.description is not None:
    #             return self.cursor.fetchall()

    #         # Confirmar los cambios de escritura.
    #         self.connection.commit()

    #         return self.cursor.lastrowid

    #     except sqlite3.Error as e:
    #         self.connection.rollback()
    #         print(f"Error SQLite: {e}")
    #         print(f"Consulta: {query}")
    #         print(f"Parámetros: {params}")
    #         raise
    def exe(self, query: str, params=None) -> None:
        """Ejecuta una consulta en la base de datos SQLite y maneja la excepción."""
        try:
            if not self.connection:
                self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            print(f"Consulta ejecutada: {query}")
            # get the id of the last inserted row
            return self.cursor.lastrowid
            # logger.debug(f"Consulta ejecutada: {query}")

        # except sqlite3.IntegrityError:
        #     print("ERROR: ID already exists in PRIMARY KEY column {}".format(query))
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad: {e}")
            print(f"Consulta: {query}")
            print(f"Parámetros: {params}")
        except sqlite3.Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            # logger.error(f"Error al ejecutar la consulta: {e}")

    def show_tables(self):
        """Muestra las tablas de la base de datos SQLite."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return self.cursor.fetchall()
        tables = self.cursor.fetchall()
        for table in tables:
            print(table[0])

    def fetch_all(self) -> list:
        """Obtiene todos los registros de una consulta."""
        return self.cursor.fetchall()

    def fetch_one(self):
        """Obtiene un solo registro de una consulta."""
        return self.cursor.fetchone()

    def fetch_many(self, size) -> list:
        """
        Fetches a specified number of records from the result set.

        Args:
            size (int): The number of records to fetch.

        Returns:
            list: A list of records fetched from the result set.
        """
        """Obtiene varios registros de una consulta."""
        return self.cursor.fetchmany(size)

    def fetch_val(self, col: int = 0):
        """Obtiene solo un valor de una columna de una consulta.

        Args:
            col (int): Índice de la columna.
        """
        try:
            return self.cursor.fetchone()[col]
        except TypeError:
            return None

    def fetch_col(self, col: int) -> list:
        """
        Fetches the values of a specified column from the result of a query.

        Args:
            col (int): The index of the column to fetch values from.

        Returns:
            list: A list containing the values of the specified column.
        """
        """Obtiene los valores de una columna de una consulta."""
        return [row[col] for row in self.cursor.fetchall()]
