import os, sys
from os.path import abspath, join, getsize
import sqlite3

def run_file_script():
    open('output.txt','w').close()
    a1, a2 = None, None
    print(f'The name of this module is: {__name__}')
    temp_path = input('\n1) Enter the path of the directory to scan:')
    q1 = input('2) Default scan will return 20 largest files, do you wish to customise this further? [Y/N]:')
    if q1.upper() in ['Y', 'YES']:
        print('\nSelect one of the customization options below:')
        q2 = input('\n- i) To scan for files by name, ENTER 1:'\
            '\n- ii) To scan for files by type (e.g. ".mp3"), ENTER 2:'\
            '\n- iii) To scan for files by name & type, ENTER 3:')
        if q2 == '1': 
            method = 'name'
            a1 = input('-- a) please enter the name (full/partial) of the file you would like to find:')
        elif q2 == '2': 
            method = 'type'
            a2 = input('-- b) please enter the file type would like to find (e.g. mp3, csv etc):')
            if a2[0]=='.': a2=a2[1:]
        elif q2 == '3': 
            method = 'name & type'
            a1 = input('-- a) please enter the name (full/partial) of the file you would like to find:')
            a2 = input('-- b) please enter the file type would like to find (e.g. mp3, csv etc):')
            if a2[0]=='.': a2=a2[1:]
        else: method = 'default'
    else: method = 'default'

    print(f'\nscanning: {temp_path} using method [{method}], (name={a1}, type={a2})...\n')

    if method in ['name','type','name & type']:
        # scan directory and store details using a SQLite db 
        # SQLite can run in-memory, no file will be created, and when the program ends, the database goes away
        connection = sqlite3.connect(':memory:')
        # define the query to create a table to hold file paths and sizes in bytes for those files
        table = 'CREATE TABLE file_table (id integer primary key, path TEXT, bytes INTEGER)'
        cursor = connection.cursor()
        cursor.execute(table)
        connection.commit()

        for top_dir, directories, files in os.walk(temp_path):
            for _file in files:
                full_path = abspath(join(top_dir, _file))
                try:
                    size = getsize(full_path)
                    query = 'INSERT INTO file_table(path, bytes) VALUES(?, ?)'
                    # the execute() method accepts a query and optionally a tuple with values 
                    # corresponding to the question marks in VALUES
                    cursor.execute(query, (full_path, size))
                    connection.commit()
                except OSError: None
        if q2 == '1': 
            query = """SELECT * from file_table WHERE path LIKE '{}' ORDER BY bytes DESC LIMIT(20)""".format('%'+a1+'%')
            query_cnt = """SELECT COUNT(*) from file_table WHERE path LIKE '{}' ORDER BY bytes DESC""".format('%'+a1+'%')
        if q2 == '2': 
            query = """SELECT * from file_table WHERE path LIKE '{}' ORDER BY bytes DESC LIMIT(20)""".format('%'+a2)
            query_cnt = """SELECT COUNT(*) from file_table WHERE path LIKE '{}' ORDER BY bytes DESC""".format('%'+a2)
        if q2 == '3': 
            query = """SELECT * from file_table WHERE path LIKE '{}' ORDER BY bytes DESC LIMIT(20)""".format('%'+a1+'%'+a2)
            query_cnt = """SELECT COUNT(*) from file_table WHERE path LIKE '{}' ORDER BY bytes DESC""".format('%'+a1+'%'+a2)
        x=1
        for i in cursor.execute(query):
            with open('output.txt', 'a') as f: 
                print(f'{x}) Path: {i[1]}, size: {i[2]:,}', file=f)
            print(f'{x}) Path: {i[1]}, size: {i[2]:,}')
            x+=1
        for i in cursor.execute(query_cnt):
            print(f'\nNumber of files found = {i[0]:,}')

    if method == 'default':
        # scan directory and store details using a dictionary 
        sizes = {}
        for top_dir, directories, files in os.walk(temp_path):
            for _file in files:
                full_path = abspath(join(top_dir, _file))
                try:
                    size = getsize(full_path)
                    sizes[full_path]=size
                except OSError: None

        sorted_results = sorted(sizes, key=sizes.get, reverse=True)
        x=1
        for path in sorted_results[:20]:
            with open('output.txt', 'a') as f: 
                print(f'{x}) Path: {path}, size: {sizes[path]:,}', file=f)
            print(f'{x}) Path: {path}, size: {sizes[path]:,}')
            x+=1
        print(f'\nNumber of files found = {len(sorted_results):,}')

    return temp_path

if __name__ == '__main__':
    output = run_file_script()

