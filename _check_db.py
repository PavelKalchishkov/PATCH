import psycopg2

c = psycopg2.connect(dbname="PATCH", user="postgres", password="4321", port=5432)
cur = c.cursor()
cur.execute("SELECT version()")
print(cur.fetchone()[0])
try:
    cur.execute("SELECT PostGIS_Version()")
    print("postgis", cur.fetchone())
except Exception as e:
    print("no postgis", type(e).__name__, e)
    c.rollback()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        c.commit()
        print("created postgis")
        cur.execute("SELECT PostGIS_Version()")
        print(cur.fetchone())
    except Exception as e2:
        print("create failed", e2)
        c.rollback()
c.close()
