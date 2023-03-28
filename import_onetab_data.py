#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : lolonao
# Created Date: 2023/03/28
# version ='0.0.1'
# ---------------------------------------------------------------------------
""" Script to import exported data from OneTab browser extension into SQLite3. I will add the ability to search by keywords or categories."""
import argparse
# import os
import sqlite3
from pathlib import Path


def create_db(db_path):
    db_exists = db_path.exists()

    if not db_exists:
        print(f'Database does not exist at {db_path}, creating new sqlite3 database.')

    create_table = 'CREATE TABLE links(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, url TEXT NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)'

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        if len(tables) == 0:
            c.execute(create_table)
        return conn, c
    except Exception as e:
        print(f'An error occurred: {e}')
        return None, None


def import_data(conn, c, file_path):
    try:
        file_exists = file_path.exists()
        if not file_exists:
            print(f'{file_path} does not exist, skipping')
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read().split('\n')
                for line in file_content:
                    line_parts = line.replace('|', '&&&').split('&&&')
                    line_parts = [part.strip() for part in line_parts]
                    if line_parts[0] and line_parts[1] and 'chrome-extension://' not in line_parts[0] and 'google.' not in line_parts[0]:
                        c.execute('SELECT * FROM links WHERE title=? AND url=?', (line_parts[0], line_parts[1]))
                        data = c.fetchone()
                        if data is None:
                            insert_query = 'INSERT INTO links (title, url) VALUES (?, ?)'
                            c.execute(insert_query, (line_parts[0], line_parts[1]))
    except Exception as e:
        print(f'An error occurred: {e}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, required=True)
    parser.add_argument('--file', type=str, nargs='+', required=True)
    args = parser.parse_args()

    ROOT = Path.cwd()
    # usage = 'Usage: onetab2sqlite --db ./onetab.db --file ./onetab-export.txt. You can pass multiple --file arguments.'

    db_path = ROOT / args.db

    conn, c = create_db(db_path)

    if conn is not None and c is not None:
        for i in args.file:
            file_path = ROOT / i
            import_data(conn, c, file_path)

        conn.commit()
        conn.close()


if __name__ == '__main__':
    main()
