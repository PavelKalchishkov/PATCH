import psycopg2

c = psycopg2.connect(dbname="PATCH", user="postgres", password="4321", host="localhost", port=5432)
c.autocommit = True
cur = c.cursor()
cur.execute(
    """
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename
    """
)
print("tables:", [r[0] for r in cur.fetchall()])
cur.execute("DROP SCHEMA public CASCADE")
cur.execute("CREATE SCHEMA public")
cur.execute("GRANT ALL ON SCHEMA public TO postgres")
cur.execute("GRANT ALL ON SCHEMA public TO public")
print("schema reset")
c.close()
