#!/bin/env python3

# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd


import time
from uuid import uuid4

import spanner_dbapi
from google.cloud import spanner_v1
from google.cloud.spanner_v1 import param_types as types


def main():
    client = spanner_v1.Client()
    ins = client.instance('benchmarking')
    if not ins.exists():
        ins.configuration_name = 'projects/' + client.project + '/instanceConfigs/regional-us-west2'
        _ = ins.create()

    db = ins.database('db1')
    if not db.exists():
        _ = db.create()

    conn = spanner_dbapi.connect(project=client.project, database=db.database_id, instance=ins.instance_id)

    nruns=50
    diffs = dict(
        ReadOnly=benchmark_read_only(db, conn, nruns),
        ReadWrite=benchmark_read_write(db, conn, nruns),
        CreateDestroyTable=benchmark_create_destroy_table(db, conn, nruns),
        Insert20Params=benchmark_insert(db, conn, nruns=nruns, field_count=20),
        Insert50Params=benchmark_insert(db, conn, nruns=nruns, field_count=50),
        Insert100Params=benchmark_insert(db, conn, nruns=nruns, field_count=100),
    )
    conn.close()

    f_v1 = open('bench_v1.txt', 'w')
    f_dbapi = open('bench_dbapi.txt', 'w')
    for benchmarkName, time_deltas_tuple in diffs.items():
        v1, dbapi = time_deltas_tuple
        for i in range(len(v1)):
            f_v1.write('Benchmark%s 1 %f ns/op\n' % (benchmarkName, v1[i]))
            f_dbapi.write('Benchmark%s 1 %f ns/op\n' % (benchmarkName, dbapi[i]))

    f_v1.close()
    f_dbapi.close()


query_information_schema = "SELECT * FROM INFORMATION_SCHEMA.TABLES as it WHERE it.TABLE_SCHEMA=''"


def benchmark_create_destroy_table(db, conn, nruns=5):
    def create_table_v1(db, n):
        names = ['T_v1_%d' % i for i in range(n)]
        stmts = []
        for table_name in names:
            sql = '''DROP TABLE ''' + table_name
            stmts.append(sql)
        try:
            _ = db.update_ddl(stmts).result()
        except Exception as e:
            pass
        _ = list(with_v1_with_snapshot(db)(query_information_schema))

        for table_name in names:
            sql = '''CREATE TABLE %s(
                    name STRING(MAX),
                    id INT64
                 ) PRIMARY KEY(id)''' % table_name
            _ = db.update_ddl([sql]).result()
        _ = list(with_v1_with_snapshot(db)(query_information_schema))

        # Now drop the tables.
        for table_name in names:
            sql = '''DROP TABLE ''' + table_name
            _ = db.update_ddl([sql]).result()
        _ = list(with_v1_with_snapshot(db)(query_information_schema))

    n_tables = 3
    v1_time_deltas = repeat_timed(nruns, create_table_v1, db, n_tables)

    def create_table_dbapi(cursor, n):
        names = ['T_dbapi_%d' % i for i in range(n)]
        for table_name in names:
            sql = '''DROP TABLE ''' + table_name
            cursor.execute(sql)

        try:
            _ = list(with_dbapi(conn)(query_information_schema))
        except Exception as e:
            pass

        for table_name in names:
            sql = '''CREATE TABLE %s(
                    name STRING(MAX),
                    id INT64
                 ) PRIMARY KEY(id)''' % table_name
            cursor.execute(sql)
        _ = list(with_dbapi(conn)(query_information_schema))

        for table_name in names:
            sql = '''DROP TABLE ''' + table_name
            cursor.execute(sql)
        _ = list(with_dbapi(conn)(query_information_schema))

    with conn.cursor() as cursor:
        dbapi_time_deltas = repeat_timed(nruns, create_table_dbapi, cursor, n_tables)
        return v1_time_deltas, dbapi_time_deltas


def benchmark_read_write(db, conn, nruns=20):
    names = ('rw_v1', 'rw_dbapi',)
    # Clear any prior remnants.
    clear_ddls = ['DROP TABLE ' + name for name in names]
    try:
        _ = db.update_ddl(clear_ddls).result()
    except Exception as e:
        pass

    create_ddls = []
    for table_name in names:
        create_ddls.append(
            '''CREATE TABLE %s(
                age INT64,
                id STRING(64),
                last_ping INT64
            ) PRIMARY KEY(id)''' % table_name)
    _ = db.update_ddl(create_ddls).result()

    # Populate the tables.
    n_items = 200
    values = [(i, '%d' % (uuid4().int & 0x7FFFFFFFFFFFFFFF),) for i in range(n_items)]
    def populate_tables(txn):
        _ = txn.insert(names[0], ['age', 'id'], values)
        _ = txn.insert(names[1], ['age', 'id'], values)
    db.run_in_transaction(populate_tables)


    def rw_v1(db):
        with db.snapshot(multi_use=True) as snapshot:
            res = list(snapshot.execute_sql('SELECT * FROM rw_v1'))
            if len(res) != n_items:
                raise Exception('rw_v1: n_items mismatch: got %d wanted %d' % (len(res), n_items))
            _ = list(snapshot.execute_sql('SELECT * from rw_v1 WHERE age <= @n',
                                            params={'n': int(n_items/2)},
                                            param_types={'n': types.INT64}))

        def finish_rw(txn):
            res = txn.execute_sql('UPDATE rw_v1 as t SET last_ping=@lp WHERE age >= @ag',
                                            params={'lp': 10, 'ag': int(n_items/3)},
                                            param_types={'lp': types.INT64, 'ag': types.INT64})
            if hasattr(res, '__iter__'):
                _ = list(res)

            _ = txn.execute_sql('DELETE FROM rw_v1 WHERE age <= @n',
                                            params={'n': int(n_items/5)},
                                            param_types={'n': types.INT64})
            res = txn.execute_sql('SELECT COUNT(*) FROM rw_v1')
            if hasattr(res, '__iter__'):
                _ = list(res)
    
        db.run_in_transaction(finish_rw)
                
    v1_time_deltas = repeat_timed(nruns, rw_v1, db)


    # Now that they have data, read and write to them.
    def rw_dbapi(cursor):
        cursor.execute('SELECT * FROM rw_dbapi')
        res = list(cursor)
        if False and len(res) != n_items:
            raise Exception('rw_dbapi: n_items mismatch: got %d wanted %d' % (len(res), n_items))
        cursor.execute('SELECT * from rw_dbapi WHERE age <= %s', (n_items/2,))
        _ = list(cursor)

        cursor.execute('UPDATE rw_dbapi as t SET last_ping=%s WHERE age >= %s', (10, n_items/3,))
        _ = cursor.rowcount

        cursor.execute('DELETE FROM rw_dbapi WHERE age <= %s', (n_items/5,))
        cursor.execute('SELECT COUNT(*) FROM rw_dbapi')

    with conn.cursor() as cursor:
        dbapi_time_deltas = repeat_timed(nruns, rw_dbapi, cursor)
        return v1_time_deltas, dbapi_time_deltas


def benchmark_read_only(db, conn, nruns=20):
    names = ('r_v1', 'r_dbapi',)
    # Clear any prior remnants.
    clear_ddls = ['DROP TABLE ' + name for name in names]
    try:
        _ = db.update_ddl(clear_ddls).result()
    except Exception as e:
        pass
    
    create_ddls = []
    for table_name in names:
        create_ddls.append(
            '''CREATE TABLE %s(
                age INT64,
                id STRING(64),
                last_ping INT64
            ) PRIMARY KEY(id)''' % table_name)
    _ = db.update_ddl(create_ddls).result()

    # Populate the tables.
    n_items = 200
    values = [(i, '%d' % (uuid4().int & 0x7FFFFFFFFFFFFFFF),) for i in range(n_items)]
    def populate_tables(txn):
        _ = txn.insert(names[0], ['age', 'id'], values)
        _ = txn.insert(names[1], ['age', 'id'], values)
    db.run_in_transaction(populate_tables)


    def r_v1(db):
        with db.snapshot(multi_use=True) as snapshot:
            res = list(snapshot.execute_sql('SELECT * FROM r_v1'))
            if len(res) != n_items:
                raise Exception('r_v1: n_items mismatch: got %d wanted %d' % (len(res), n_items))
            _ = list(snapshot.execute_sql('SELECT * from r_v1 WHERE age <= @n',
                                            params={'n': int(n_items/2)}, param_types={'n': types.INT64}))
            _ = list(snapshot.execute_sql(query_information_schema))
            _ = list(snapshot.execute_sql('SELECT COUNT(*) FROM r_v1'))
                
    v1_time_deltas = repeat_timed(nruns, r_v1, db)


    def r_dbapi(cursor):
        cursor.execute('SELECT * FROM r_dbapi')
        res = list(cursor)
        if len(res) != n_items:
            raise Exception('r_dbapi: n_items mismatch: got %d wanted %d' % (len(res), n_items))
        cursor.execute('SELECT * from r_dbapi WHERE age <= %s', (n_items/2,))
        _ = list(cursor)
        cursor.execute(query_information_schema)
        _ = list(cursor)
        cursor.execute('SELECT COUNT(*) FROM r_dbapi')
        _ = list(cursor)

    with conn.cursor() as cursor:
        dbapi_time_deltas = repeat_timed(nruns, r_dbapi, cursor)
        return v1_time_deltas, dbapi_time_deltas

    
def uniq_id():
    return uuid4().int & 0x7FFFFFFFFFFFFFFF


def benchmark_insert(db, conn, nruns=100, field_count=50):
    '''
    Test out: INSERT INTO T (fields...) VALUES (%s, LOWER(%s), UPPER(%s), ...)
    '''
    v1_table_name, dbapi_table_name = 'INS_v1', 'INS_dbapi'
    table_names = [v1_table_name, dbapi_table_name]

    try:
        drop_ddls = ['DROP TABLE %s' % table_name for table_name in table_names]
        _ = db.update_ddl(drop_ddls).result()
    except Exception as e:
        pass

    def create_table(table_name):
        fields_txt = ',\n'.join(['F%d STRING(MAX)'%(i) for i in range(field_count)])
        return 'CREATE TABLE %s (\n%s\n) PRIMARY KEY (F0)' % (table_name, fields_txt)

    ddl = [create_table(table_name) for table_name in (v1_table_name, dbapi_table_name)]
    _ = db.update_ddl(ddl).result()

    v1_table_name, dbapi_table_name = table_names
    fields_in_insert = ','.join(['F%d'%(i) for i in range(field_count)])

    def insert_v1(db):
        def insert_it(txn):
            columns = []
            for i  in range(field_count):
                column_str = '@a%d' % i
                if i%3 == 0:
                    column_str = 'UPPER(%s)' % column_str
                elif i%2 == 0:
                    column_str = 'LOWER(%s)' % column_str
                columns.append(column_str)

            fields_str = ','.join(['F%d'%(i) for i in range(field_count)])
            columns_str = ','.join(columns)
            sql = 'INSERT INTO %s (%s) VALUES (%s)'  % (v1_table_name, fields_str, columns_str)
            for x in range(1):
                params={'a%d'%(i): '%s'%(uniq_id()) for i in range(field_count)}
                param_types={'a%d'%(i): types.STRING for i in range(field_count)}
                res = txn.execute_sql(sql, params=params, param_types=param_types)
                if hasattr(res, '__iter__'):
                    _ = list(res)
        db.run_in_transaction(insert_it)

        def delete_all(txn):
            res = txn.execute_sql('DELETE FROM ' + v1_table_name + ' WHERE 1=1')
            if hasattr(res, '__iter__'):
                _ = list(res)
            _ = list(txn.execute_sql('SELECT 1'))
        db.run_in_transaction(delete_all)

    v1_time_deltas = repeat_timed(nruns, insert_v1, db)

    def insert_dbapi(cursor):
        pyfmt_args = []
        for i  in range(field_count):
            pyfmt_arg = '%s'
            if i%3 == 0:
                pyfmt_arg = 'UPPER(%s)'
            elif i%2 == 0:
                pyfmt_arg = 'LOWER(%s)'
            pyfmt_args.append(pyfmt_arg)
        columns_str = ','.join(pyfmt_args)
        sql = 'INSERT INTO %s (%s) VALUES (%s)' % (dbapi_table_name, fields_in_insert, columns_str)
        args=['a%s' % (uniq_id()) for i in range(field_count*1)]
        cursor.execute(sql, args)
        cursor.execute('DELETE FROM ' +dbapi_table_name)
        cursor.execute('SELECT 1')

    with conn.cursor() as cursor:
        dbapi_time_deltas = repeat_timed(nruns, insert_dbapi, cursor)
        return v1_time_deltas, dbapi_time_deltas


def with_v1_with_snapshot(db):
    def do(sql, *args, **kwargs):
        with db.snapshot() as snapshot:
            return snapshot.execute_sql(sql, *args, **kwargs)

    return do


def with_dbapi(conn):
    def do(sql, *args, **kwargs):
        with conn.cursor() as cursor:
            cursor.execute(sql, *args, **kwargs)
            return list(cursor)

    return do


def repeat_timed(n, fn, *args, **kwargs):
    time_deltas = []
    for i in range(n):
        time_delta, _, _ = timed(fn, *args, **kwargs)
        time_deltas.append(time_delta)
    return time_deltas


def timed(fn, *args, **kwargs):
    start = time.time_ns()
    res = None
    exc = None
    try:
        res = fn(*args, **kwargs)
    except Exception as e:
        exc = e
    finally:
        diff = time.time_ns() - start
        if exc:
            raise exc
        return diff, res, exc


if __name__ == '__main__':
    main()