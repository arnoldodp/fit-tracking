from sqlalchemy import text
from database.database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, username, email FROM users LIMIT 10"))
        print("Conexión exitosa a la base de datos Supabase. Usuarios encontrados:")
        for row in result:
            print(row)
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}") 