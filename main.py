from langchain import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chat_models import ChatOpenAI  # Usar el modelo de chat de OpenAI, versión actual
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave de API de OpenAI y la URL de la base de datos PostgreSQL
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PG_DB_URL = os.environ.get('PG_DB_URL')

# Establecer la clave de API en el entorno
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Crear la conexión a la base de datos
db = SQLDatabase.from_uri(PG_DB_URL)

# Crear el modelo LLM usando la versión recomendada
llm = ChatOpenAI(temperature=0)

# Crear la cadena de base de datos con el método correcto
db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=False)

def generar_consulta(natural_query):
    """
    Genera una consulta SQL a partir de una consulta en lenguaje natural y ajusta la sintaxis si es necesario.
    """
    try:
        # Obtener la información de las tablas de la base de datos
        table_info = db.get_table_info()
        
        # Crear los parámetros necesarios para generar la consulta SQL
        inputs = {
            'input': natural_query,
            'table_info': table_info,
            'top_k': 1  # Limita las opciones para mantener las más relevantes
        }
        
        # Usa el modelo para traducir la consulta en lenguaje natural a SQL
        sql_query = db_chain.llm_chain.predict(**inputs)
        
        # Ajustar la consulta para asegurar compatibilidad con SQL Server
        sql_query = ajustar_sintaxis(sql_query)
        return sql_query
    except Exception as e:
        print("Error al generar la consulta SQL:", e)
        return None

def ajustar_sintaxis(sql_query):
    """
    Ajusta la sintaxis de la consulta SQL para asegurar compatibilidad con SQL Server.
    """
    # Reemplazar comillas dobles por corchetes si es necesario
    sql_query = sql_query.replace("\"", "[")
    sql_query = sql_query.replace("[[", "[")  # Asegurar que no haya corchetes duplicados
    sql_query = sql_query.replace("]", "]")  # Mantener el cierre de corchetes correcto

    # Ajustar otros posibles problemas de sintaxis si es necesario
    if "SELECT TOP 1" in sql_query:
        sql_query = sql_query.replace("SELECT TOP 1", "SELECT TOP 1")

    return sql_query

def ejecutar_consulta(sql_query):
    """
    Ejecuta la consulta SQL en la base de datos.
    """
    try:
        # Ejecutar la consulta SQL usando la base de datos
        resultado = db.run(sql_query)
        return resultado
    except Exception as e:
        print("Error al ejecutar la consulta SQL:", e)
        return None

def mostrar_resultado(resultado):
    """
    Muestra solo el resultado de la consulta SQL.
    """
    if resultado is not None and len(resultado) > 0:
        # Asumiendo que el resultado es una lista de filas (tuplas)
        print(resultado[0][0])


# Ejemplo de uso
consulta_natural = " decime el tipo de feriado que mas esta en la tabla feriado"
consulta_sql = generar_consulta(consulta_natural)

if consulta_sql:
    resultado = ejecutar_consulta(consulta_sql)
    mostrar_resultado(resultado)
