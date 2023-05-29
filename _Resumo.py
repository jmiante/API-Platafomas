import sqlite3

insert = False

with sqlite3.connect('_Resumo.sqlite') as conn:
    cursor = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS resumo (
        data_criacao date not null,
        api varchar(100) not null,
        nome varchar(200) not null,
        pyinstaller varchar(200) not null
    )
    """
    cursor.execute(sql)
    conn.commit()


data = [
    ['2023-05-13', '000.001', 'Relatório Mega - Fiscal', 'pyinstaller 000001_relatorio_mega_fiscal.py --onefile --name="Relatório Mega - Fiscal"'],
    ['2023-05-15', '000.002', 'Relatório Mega - Financeiro', 'pyinstaller 000002_relatorio_mega_financeiro.py --onefile --name="Relatório Mega - Financeiro"'],
]
if insert:
    with sqlite3.connect('_Resumo.sqlite') as conn:
        cursor = conn.cursor()
        value = data[-1]
        sql = f"INSERT INTO resumo VALUES ('{value[0]}', '{value[1]}', '{value[2]}', '{value[3]}')"
        cursor.execute(sql)
        conn.commit()


with sqlite3.connect('_Resumo.sqlite') as conn:
    cursor = conn.cursor()
    sql = f"SELECT * FROM resumo"
    cursor.execute(sql)
    fetch = cursor.fetchall()
    conn.commit()

for f in fetch:
    print(f)