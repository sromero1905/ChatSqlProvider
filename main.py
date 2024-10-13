from langchain import SQLDatabase, OpenAI
from langchain_experimental.sql import SQLDatabaseChain
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

# Crear el modelo LLM
llm = OpenAI(temperature=0)

# Crear la cadena de base de datos
db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

result = db_chain.run("dame la materia con mas carga semanal")
print(result)  # Imprimir el resultado