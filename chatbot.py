def get_knowledge_base():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM knowledge_base")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]