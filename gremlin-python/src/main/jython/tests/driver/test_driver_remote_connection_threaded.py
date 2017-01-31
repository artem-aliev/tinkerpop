'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''
import sys
from threading import Thread

import pytest
from six.moves import queue

from gremlin_python.driver.driver_remote_connection import (
    DriverRemoteConnection)
from gremlin_python.structure.graph import Graph

__author__ = 'David M. Brown (davebshow@gmail.com)'


def test_conns_in_threads(remote_connection):
    q = queue.Queue()
    child = Thread(target=_executor, args=(q, None))
    child2 = Thread(target=_executor, args=(q, None))
    child.start()
    child2.start()
    for x in range(2):
        success = q.get()
        assert success == 'success!'
    child.join()
    child2.join()

def test_conn_in_threads(remote_connection):
    q = queue.Queue()
    child = Thread(target=_executor, args=(q, remote_connection))
    child2 = Thread(target=_executor, args=(q, remote_connection))
    child.start()
    child2.start()
    for x in range(2):
        success = q.get()
        assert success == 'success!'
    child.join()
    child2.join()

def _executor(q, conn):
    close = False
    if not conn:
        # This isn't a fixture so close manually
        close = True
        conn = DriverRemoteConnection(
            'ws://localhost:45940/gremlin', 'g', pool_size=4)
    try:
        g = Graph().traversal().withRemote(conn)
        future = g.V().promise()
        t = future.result()
        assert len(t.toList()) == 6
    except:
        q.put(sys.exc_info()[0])
    else:
        q.put('success!')
        # Close conn
        if close:
            conn.close()
