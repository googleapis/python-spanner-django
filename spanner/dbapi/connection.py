# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .cursor import AS_BATCH, AS_TRANSACTION, OP_DELETE, OP_INSERT, OP_UPDATE, Cursor
from .exceptions import Error


class Connection(object):
    def __init__(self, db_handle):
        self.__dbhandle = db_handle
        self.__closed = False
        self.__ops = []

    def __raise_if_already_closed(self):
        """
        Raises an exception if attempting to use an already closed connection.
        """
        if self.__closed:
            raise Error('attempting to use an already closed connection')

    def close(self):
        self.commit()
        self.__raise_if_already_closed()
        self.__dbhandle = None
        self.__closed = True

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        return self.close()

    def commit(self):
        if not self.__ops:
            return

        ops = self.__ops[:]
        self.__ops = []

        while ops:
            head_op = ops[0]
            head_op_type = head_op[0]
            rest = ops[1:]
            shave_index = 0
            same_ops = [head_op]
            for i, op in enumerate(rest):
                cur_typ = op[0]
                if cur_typ != head_op_type:
                    break
                else:
                    same_ops.append(op)

            ops = ops[len(same_ops):]

            if head_op_type == AS_BATCH:
                self.__run_batches(same_ops)
            elif head_op_type == AS_TRANSACTION:
                self.__run_transactions(same_ops)
            else:
                raise Exception('Unknown type: {typ}'.format(typ=head_op_type))

    def __run_batches(self, ops):
        with self.__dbhandle.batch() as batch:
            for call_op in ops:
                op, sql, table, columns, values = call_op[1]
                if op == OP_DELETE:
                    batch.delete(table)
                elif op == OP_INSERT:
                    batch.insert(table, columns, values)
                elif op == OP_UPDATE:
                    batch.update(table, columns, values)

    def __run_transactions(self, ops):
        self.__dbhandle.run_in_transaction(self.__do_run_transactions, ops)

    def __do_run_transactions(self, txn, ops):
        for call_op in ops:
            fn, sql, params, param_types, kwargs = call_op[1]
            fn(txn, sql, params, param_types)

    def _snapshot(self):
        return self.__dbhandle.snapshot()

    def rollback(self):
        # We don't manage transactions.
        pass

    def append_to_batch_stack(self, op):
        self.__ops.append(op)

    def cursor(self):
        return Cursor(self)

    def update_ddl(self, ddl_statements):
        """
        Runs the list of Data Definition Language (DDL) statements on the specified
        database. Note that each DDL statement MUST NOT contain a semicolon.

        Args:
            ddl_statements: a list of DDL statements, each without a semicolon.

        Returns:
            google.api_core.operation.Operation
        """
        # Synchronously wait on the operation's completion.
        return self.__dbhandle.update_ddl(ddl_statements).result()
