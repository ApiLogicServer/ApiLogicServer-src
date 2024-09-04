import sqlite3
import sys
from pathlib import Path

def create_sqlite(xls_fn) -> str:
    import pandas as pd
    excel_file = pd.ExcelFile(xls_fn)
    sheet_names = excel_file.sheet_names
    xls_path = Path(xls_fn)
    if not xls_path.exists():
        print("File does not exist")
        return
    sqlite_path = xls_path.parent / 'db.sqlite'
    conn = sqlite3.connect(str(sqlite_path))

    for sheet_name in sheet_names:
        print(f"Sheet: {sheet_name}")
        df = pd.read_excel(xls_fn, sheet_name=sheet_name)
        leftmost_column = df.columns[0]
        if df[leftmost_column].is_unique:
            df.to_sql(sheet_name, conn, if_exists='replace', index=False, 
                      dtype={leftmost_column: 'PRIMARY KEY'})
        else:
            df.insert(0, 'id', range(1, len(df) + 1))
            df.to_sql(sheet_name, conn, if_exists='replace', index=False, 
                      dtype={'id': 'INTEGER PRIMARY KEY AUTOINCREMENT'})
        

    conn.commit()
    conn.close()
    return f"sqlite:///{sqlite_path}"


if __name__ == "__main__":
    xls_fn = sys.argv[1]
    create_sqlite(xls_fn)