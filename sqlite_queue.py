"""
Implements a reliable, persistent, thread-safe queue using SQLite.
'reliable' means that items popped from the queue that have not completed
processing for whatever reason are restored to the queue when it is opened 
again.  'persistent' means saved to disk so items persist between runs of the
process.
Modified from the code presented at (reliability added):  
    http://flask.pocoo.org/snippets/88/
"""
import os, sqlite3
from pickle import loads, dumps
from time import sleep
try:
    from _thread import get_ident
except ImportError:
    from _dummy_thread import get_ident


class SqliteReliableQueue(object):

    # SQL Statements needed for Queue commands
    _create_queue = (
            'CREATE TABLE IF NOT EXISTS queue ' 
            '('
            '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
            '  item BLOB'
            ')'
            )
    _create_processing = (
            'CREATE TABLE IF NOT EXISTS processing ' 
            '('
            '  id INTEGER PRIMARY KEY,'
            '  item BLOB'
            ')'
            )
    _count = 'SELECT COUNT(*) FROM queue'
    _iterate = 'SELECT id, item FROM queue'
    _append = 'INSERT INTO queue (item) VALUES (?)'
    _write_lock = 'BEGIN IMMEDIATE'
    _popleft_get = (
            'SELECT id, item FROM queue '
            'ORDER BY id LIMIT 1'
            )
    _popleft_del = 'DELETE FROM queue WHERE id = ?'
    _peek = (
            'SELECT item FROM queue '
            'ORDER BY id LIMIT 1'
            )
    _processing_append = 'INSERT INTO processing (id, item) VALUES (?, ?)'
    _processing_del = 'DELETE FROM processing WHERE id = ?'
    _processing_clear = 'DELETE FROM processing'
    _processing_iterate = 'SELECT id, item FROM processing'

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self._connection_cache = {}
        with self._get_conn() as conn:
            # if queue and processing tables do not exist, create them
            conn.execute(self._create_queue)
            conn.execute(self._create_processing)

            # transfer any entries from the processing list back into the
            # queue and clear the processing list.
            for id, obj_buffer in conn.execute(self._processing_iterate):
                # append method does not work here, perhaps due to running
                # a second 'with' statement.  Use direct SQL statemen instead.
                conn.execute(self._append, (obj_buffer,))
            conn.execute(self._processing_clear)

    def __len__(self):
        with self._get_conn() as conn:
            l = conn.execute(self._count).next()[0]
        return l

    def __iter__(self):
        with self._get_conn() as conn:
            for id, obj_buffer in conn.execute(self._iterate):
                yield loads(obj_buffer)

    def __str__(self):
        res = 'Queue:\n'
        for item in self:
            res += '%s\n' % item
        res += 'Processing:\n'
        for item in self.iter_processing():
            res += '%s\n' % item
        return res            

    def _get_conn(self):
        """Gets a connection from a pool based on the ID of the thread calling
        this method.
        """
        id = get_ident()
        if id not in self._connection_cache:
            self._connection_cache[id] = sqlite3.Connection(self.path, 
                    timeout=60)
        return self._connection_cache[id]
    
    def append(self, obj):
        """Adds an item to the queue.
        """
        obj_pkl = dumps(obj, 2)
        with self._get_conn() as conn:
            conn.execute(self._append, (obj_pkl,))
            # the 'with' statement commits the insert.

    def popleft(self, sleep_wait=True):
        keep_pooling = True
        wait = 0.5       # initial wait time for new queue items
        max_wait = 5.0   # seconds of maximum wait for item in queue
        tries = 0
        with self._get_conn() as conn:
            id = None
            while keep_pooling:
                # need to make sure another thread does not pop the same item.
                conn.execute(self._write_lock)
                cursor = conn.execute(self._popleft_get)
                try:
                    id, obj_buffer = next(cursor)
                    keep_pooling = False
                except StopIteration:
                    conn.commit() # unlock the database
                    if not sleep_wait:
                        keep_pooling = False
                        continue
                    tries += 1
                    sleep(wait)
                    wait = min(max_wait, tries/2.0 + wait)
            if id:
                conn.execute(self._popleft_del, (id,))
                conn.execute(self._processing_append, (id, obj_buffer))
                return id, loads(obj_buffer)
        return None, None

    def peek(self):
        """Returns next item in queue but does not remove if from the queue.
        """
        with self._get_conn() as conn:
            cursor = conn.execute(self._peek)
            try:
                return loads(cursor.next()[0])
            except StopIteration:
                return None
                
    def finished(self, id):
        """Call when finished processing an item.  This will delete the item
        from the 'processing' list.  'id' is the id # of the item.
        """
        with self._get_conn() as conn:
            conn.execute(self._processing_del, (id,))
            
    def iter_processing(self):
        """Iterator returning items from the processing list.
        """
        with self._get_conn() as conn:
            for id, obj_buffer in conn.execute(self._processing_iterate):
                yield loads(obj_buffer)
        