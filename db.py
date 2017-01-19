"""
Надо выводить не версионированные записи и головы версионированных
"""
import pickle
from aes import AESCipher
from typing import List, Dict, Tuple, Union, Any
import os
import uuid
from datetime import datetime


def make_uuid():
    return uuid.uuid1()


class Record(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TemporaryRecord(Record):
    def __init__(self, record: Record):
        Record.__init__(self)
        self.record = record


class PermanentRecord(Record):
    enc_sig = 0

    def __init__(self, record: Record):
        Record.__init__(self)
        self.record = record

    def to_bytes(self):
        return pickle.dumps(self.record)

    # def from_bytes(self, data: bytes):
    #     self.record = pickle.loads(data)

    @staticmethod
    def from_bytes(data: bytes):
        return pickle.loads(data)


class EncryptedRecord(PermanentRecord):
    enc_sig = 1

    def __init__(self, record: Record, password_getter):
        PermanentRecord.__init__(self, record)
        self.password_getter = password_getter

    def to_bytes(self):
        aes_cipher = AESCipher(self.password_getter())
        return aes_cipher.encrypt_bytes(pickle.dumps(self.record))

    # def from_bytes(self, data: bytes):
    #     aes_cipher = AESCipher(self.password_getter())
    #     self.record = pickle.loads(aes_cipher.decrypt(data))

    @staticmethod
    def from_bytes(data: bytes, password_getter):
        aes_cipher = AESCipher(password_getter())
        return pickle.loads(aes_cipher.decrypt_bytes(data))


class DeleteMark(Record):
    def __init__(self, uid):
        """
        uuid must point to some record or to RevertMark
        """
        Record.__init__(self)
        self.uid = uid

    def __str__(self):
        return "DeleteMark: %s" % str(self.uid)


class RevertMark(Record):
    def __init__(self, uid):
        """
        uuid must point to DeleteMark
        """
        Record.__init__(self)
        self.uid = uid

    def __str__(self):
        return "RevertMark: %s" % str(self.uid)


class Category(Record):
    def __init__(self, title: str):
        Record.__init__(self)
        self.title = title

    def __str__(self):
        return "Category: %s" % self.title


class Note(Record):
    def __init__(self, title: str, text: str,
                 categories: Union[List[uuid.UUID], None]=None):
        Record.__init__(self)
        self.title = title
        self.text = text
        if categories is None:
            self.categories = []
        else:
            self.categories = categories

    def __str__(self):
        return "Note: %s %s" % (self.title, self.text)


class Task(Record):
    def __init__(self, title: str, done: bool=False,
                 begin: Union[datetime, None]=None, deadline: Union[datetime, None]=None,
                 categories: Union[List[uuid.UUID], None]=None):
        Record.__init__(self)
        self.title = title
        self.done = done
        self.begin = begin
        self.deadline = deadline
        if categories is None:
            self.categories = []
        else:
            self.categories = categories

    def __str__(self):
        return "Task: %s%s" % ('✓ ' if self.done else '', self.title)


class BookmarkURL(Record):
    def __init__(self, title: str, url: str):
        Record.__init__(self)
        self.title = title
        self.url = url

    def __str__(self):
        return "BookmarkURL: %s %s" % (self.title, self.url)


class Project(Category):
    def __init__(self, title: str, description: str):
        Category.__init__(self, title)
        self.description = description

    def __str__(self):
        return "Project: %s %s" % (self.title, self.description)


class Target(Category):
    def __init__(self, title: str, description: str):
        Category.__init__(self, title)
        self.description = description

    def __str__(self):
        return "Target: %s %s" % (self.title, self.description)


class Password(Record):
    def __init__(self, service: str, login: str, password: str):
        Record.__init__(self)
        self.service = service
        self.login = login
        self.password = password

    def __str__(self):
        return "Password: %s@%s" % (self.login, self.service)


class VersionedRecord(Record):
    def __init__(self, record: Record, created: datetime, uid: uuid.UUID, *parents: List[uuid.UUID]):
        Record.__init__(self)
        self.record = record
        self.uuid = uid
        self.created = created
        self.parents = parents


class DataBase(object):
    """
    Database:
        Some data in memory only
        Some data in memory and on disk

        ruid is a key in db.index, member of db.keys()
        vuid is a key in db.versions
    """

    class IndexRecord(object):
        def __init__(self, uid, size, offset, enc_domain):
            self.uid, self.size, self.offset, self.enc_domain = uid, size, offset, enc_domain

    def __init__(self, file_name: str=None, password_getter=None):
        self.file_name = file_name      # type: str
        self.password_getter = password_getter
        self.index = {}                 # type: Dict[uuid.UUID, Tuple[int, int]]
        self.versions = {}              # type: Dict[uuid.UUID, Dict[uuid.UUID, Tuple[uuid.UUID]]]
        self.parents = {}               # type: Dict[uuid.UUID, Dict[uuid.UUID, List[uuid.UUID]]]

        self.marks = {}                 # type: Dict[uuid.UUID, Any[None, DeleteMark, RevertMark]]
        self.who_delete = {}            # type: Dict[uuid.UUID, uuid.UUID]
        self.who_revert = {}            # type: Dict[uuid.UUID, uuid.UUID]

        if file_name is not None:
            # index file
            try:
                db_stat = os.stat(file_name)
                length = db_stat.st_size
                with open(file_name, 'rb') as df:
                    while df.tell() < length:
                        uid = uuid.UUID(bytes=df.read(16))
                        size = int.from_bytes(df.read(4), byteorder='big')
                        enc_domain = int.from_bytes(df.read(1), byteorder='big')
                        offset = df.tell()
                        self.index[uid] = DataBase.IndexRecord(uid, size, offset, enc_domain)
                        data = df.read(size)
                        if enc_domain == 0:
                            current_record = PermanentRecord.from_bytes(data)
                        elif enc_domain == 1:
                            current_record = EncryptedRecord.from_bytes(data, self.password_getter)
                        else:
                            raise ValueError('Wrong enc_domain %s %s' %
                                             (str(type(enc_domain))), str(enc_domain))
                        if isinstance(current_record, VersionedRecord):
                            ruid = current_record.uuid
                            parents = current_record.parents
                            if ruid in self.versions:
                                self.versions[ruid][uid] = parents
                            else:
                                self.versions[ruid] = {uid: parents}

                        if isinstance(current_record, DeleteMark):
                            self.marks[uid] = current_record
                            self.who_delete[current_record.uid] = uid
                        elif isinstance(current_record, RevertMark):
                            self.marks[uid] = current_record
                            self.who_revert[current_record.uid] = uid
                        else:
                            self.marks[uid] = None

            except FileNotFoundError:
                pass

            # DeleteMarks and RevertMarks not listed in this directory
            self.actual = {}  # type: Dict[uuid.UUID, bool]

            for uid in self.index.keys():
                # if record is not DeleteMark or RevertMark
                if self.marks[uid] is None:
                    actual = True
                    current_uid = uid
                    while True:
                        if current_uid in self.who_delete:
                            actual = False
                            current_uid = self.who_delete[current_uid]
                        elif current_uid in self.who_revert:
                            actual = True
                            current_uid = self.who_revert[current_uid]
                        else:
                            break
                    self.actual[uid] = actual

            for uid, version in self.versions.items():
                parents = {}
                for k, vv in version.items():
                    for v in vv:
                        if v in parents:
                            parents[v].append(k)
                        else:
                            parents[v] = [k, ]
                self.parents[uid] = parents

    def __getitem__(self, item: uuid.UUID) -> Record:
        record = self.index[item]
        if isinstance(record, DataBase.IndexRecord):
            with open(self.file_name, 'rb') as df:
                df.seek(record.offset)
                data = df.read(record.size)
                if record.enc_domain == 0:
                    return PermanentRecord.from_bytes(data)
                elif record.enc_domain == 1:
                    return EncryptedRecord.from_bytes(data, self.password_getter)
                else:
                    raise ValueError('Wrong enc_domain %s %s' %
                                     (str(type(record.enc_domain)), str(record.enc_domain)))
        elif isinstance(record, TemporaryRecord):
            return record.record

    def append(self, value: Record) -> uuid.UUID:
        """
        Если value PermanentRecord, сохранить контент в файл, в индекс добавить IndexRecord
        Если value TemporaryRecord, в index добавить саму запись
        :param value:
        :return:
        """

        # TODO change dicts if adding DeleteMark or RevertMark

        ruid = make_uuid()
        if isinstance(value, EncryptedRecord):
            data = value.to_bytes()
            size = len(data)
            with open(self.file_name, 'ab') as df:
                df.write(ruid.bytes)
                df.write(size.to_bytes(4, byteorder='big'))
                df.write(int.to_bytes(EncryptedRecord.enc_sig, 1, byteorder='big'))
                offset = df.tell()
                df.write(data)
            self.index[ruid] = DataBase.IndexRecord(ruid, size, offset, EncryptedRecord.enc_sig)
        elif isinstance(value, PermanentRecord):
            data = value.to_bytes()
            size = len(data)
            with open(self.file_name, 'ab') as df:
                df.write(ruid.bytes)
                df.write(size.to_bytes(4, byteorder='big'))
                df.write(int.to_bytes(PermanentRecord.enc_sig, 1, byteorder='big'))
                print("Save permanent record", len(ruid.bytes), size.to_bytes(4, byteorder='big'), int.to_bytes(PermanentRecord.enc_sig, 1, byteorder='big'))
                offset = df.tell()
                df.write(data)
            self.index[ruid] = DataBase.IndexRecord(ruid, size, offset, PermanentRecord.enc_sig)
        elif isinstance(value, TemporaryRecord):
            self.index[ruid] = value.record
        else:
            raise ValueError('only PermanentRecord or TemporaryRecord can be appended')
        return ruid

    def get_versions(self, ruid: uuid.UUID) -> Dict[uuid.UUID, Tuple]:
        return self.versions[ruid]

    def save_version(self, value: Record, created: datetime, ruid: uuid.UUID, *parents: List[uuid.UUID]):
        return self.append(VersionedRecord(value, created, ruid, *parents))


class PIMDB(object):
    def __init__(self, file_name: str=None, password_getter=None):
        self.db = DataBase(file_name=file_name, password_getter=password_getter)

    def __getitem__(self, item: uuid.UUID) -> Record:
        return self.db[item]

    def append(self, value: Record) -> uuid.UUID:
        return self.db.append(value)

    def add_plain_record(self, record: Record):
        return self.db.append(PermanentRecord(record))

    def add_versioned_record(self, record: Record, vuid: uuid.UUID=None, *parents: List[uuid.UUID]):
        # FIXME only parents argument needed
        if vuid is None:
            vuid = make_uuid()
            note_ruid = self.db.append(PermanentRecord(VersionedRecord(record, datetime.now(), vuid)))
        else:

            note_ruid = self.db.append(PermanentRecord(VersionedRecord(record, datetime.now(),
                                                                       vuid, *parents)))
        return note_ruid

    def add_encrypted_plain_record(self, record: Record):
        return self.db.append(PermanentRecord(EncryptedRecord(record, self.db.password_getter)))

    def add_encrypted_versioned_record(self, record: Record, vuid: uuid.UUID=None, *parents: List[uuid.UUID]):
        # FIXME only parents argument needed
        if vuid is None:
            vuid = make_uuid()
            note_ruid = self.db.append(PermanentRecord(EncryptedRecord(VersionedRecord(record, datetime.now(), vuid),
                                                                       self.db.password_getter)))
        else:

            note_ruid = self.db.append(PermanentRecord(EncryptedRecord(VersionedRecord(record, datetime.now(),
                                                                                       vuid, *parents),
                                                                       self.db.password_getter)))
        return note_ruid

    def delete_plain_record(self, ruid: uuid.UUID):
        return self.db.append(PermanentRecord(DeleteMark(ruid)))

    def revert_plain_record(self, ruid: uuid.UUID):
        return self.db.append(PermanentRecord(RevertMark(ruid)))

    def delete_versioned_record(self, vuid: uuid.UUID, ruid: uuid.UUID):
        if ruid not in self.db.index.keys():
            raise ValueError('record uid %s not in DB' % ruid)
        if vuid not in self.db.versions:
            raise ValueError('version uid %s not in version index' % vuid)

        task_record = self.db[ruid]
        if not isinstance(task_record, VersionedRecord):
            raise ValueError('specified record %s not a VersionedRecord' % ruid)
        if not isinstance(task_record.record, DeleteMark):
            delete_mark_uid = self.db.append(PermanentRecord(VersionedRecord(DeleteMark(ruid), datetime.now(),
                                                                             vuid, ruid)))
            return delete_mark_uid
        else:
            return ruid

    def revert_versioned_record(self, vuid: uuid.UUID, ruid: uuid.UUID):
        if ruid not in self.db.index.keys():
            raise ValueError('record uid %s not in DB' % ruid)
        if vuid not in self.db.versions:
            raise ValueError('version uid %s not in version index' % vuid)

        task_record = self.db[ruid]
        if not isinstance(task_record, VersionedRecord):
            raise ValueError('specified record %s not a VersionedRecord' % ruid)
        if isinstance(task_record.record, DeleteMark):
            return self.db.append(PermanentRecord(VersionedRecord(RevertMark(ruid), datetime.now(),
                                                                  vuid, ruid)))
        else:
            return None

    def done_plain_task(self, ruid: uuid.UUID):
        if ruid not in self.db.index.keys():
            raise ValueError('uid %s not in database' % ruid)
        task_record = self.db[ruid]
        if not isinstance(task_record, Task):
            raise ValueError('Records with uid %s is not a task' % ruid)
        if not task_record.done:
            task_record.done = True
            self.db.append(PermanentRecord(DeleteMark(ruid)))
            return self.db.append(PermanentRecord(task_record))
        else:
            return None

    def undone_plain_task(self, ruid: uuid.UUID):
        if ruid not in self.db.index.keys():
            raise ValueError('uid %s not in database' % ruid)
        task_record = self.db[ruid]
        if not isinstance(task_record, Task):
            raise ValueError('Records with uid %s is not a task' % ruid)
        if task_record.done:
            task_record.done = False
            self.db.append(PermanentRecord(DeleteMark(ruid)))
            return self.db.append(PermanentRecord(task_record))
        else:
            return None

    def done_versioned_task(self, vuid: uuid.UUID, ruid: uuid.UUID):
        if ruid not in self.db.versions:
            raise ValueError('uid %s not in database' % ruid)
        task_record = self.db[vuid]
        if not isinstance(task_record, VersionedRecord):
            raise ValueError('specified with %s record is not versioned record' % str(vuid))
        if task_record.uuid != ruid:
            raise ValueError('specified with %s record has uid not equals to specified uid %s' %
                             (str(vuid), str(ruid)))
        if not isinstance(task_record.record, Task):
            raise ValueError('specified with %s record is not versioned task' % str(vuid))
        task = task_record.record
        if not task.done:
            task.done = True
            return self.db.append(PermanentRecord(VersionedRecord(task, datetime.now(), ruid, vuid)))
        else:
            return None

    def undone_versioned_task(self, vuid: uuid.UUID, ruid: uuid.UUID):
        if ruid not in self.db.index.keys():
            raise ValueError('uid %s not in database' % ruid)
        if vuid not in self.db.versions:
            raise ValueError('uid %s not version' % vuid)
        task_record = self.db[ruid]
        if not isinstance(task_record, VersionedRecord):
            raise ValueError('specified with %s record is not versioned record' % str(vuid))
        if task_record.uuid != ruid:
            raise ValueError('specified with %s record has uid not equals to specified uid %s' %
                             (str(vuid), str(ruid)))
        if not isinstance(task_record.record, Task):
            raise ValueError('specified with %s record is not versioned task' % str(vuid))
        task = task_record.record
        if task.done:
            task.done = False
            return self.db.append(PermanentRecord(VersionedRecord(task, datetime.now(), ruid, vuid)))
        else:
            return None

    def list_all(self):
        for ruid in self.db.index.keys():
            yield ruid, self.db[ruid]

    def list_marks(self):
        for ruid in self.db.index.keys():
            if ruid in self.db.marks and self.db.marks[ruid] is not None:
                yield ruid, self.db.marks[ruid]

    def list_not_marks(self):
        for ruid in self.db.index.keys():
            if self.db.marks[ruid] is None:
                yield ruid, self.db[ruid]

    def is_plain_actual(self, ruid: uuid.UUID):
        return ruid in self.db.actual and self.db.actual[ruid]

    def is_plain_deleted(self, ruid: uuid.UUID):
        return ruid in self.db.actual and not self.db.actual[ruid]

    def list_plain(self):
        for ruid in self.db.index.keys():
            if self.db.marks[ruid] is None:
                data = self.db[ruid]
                if not isinstance(data, VersionedRecord):
                    yield ruid, data

    def list_versioned(self):
        for vuid in self.db.versions.keys():
            current_versions = self.db.versions[vuid]
            current_parents = self.db.parents[vuid]
            show = False
            for k, p in current_versions.items():
                if k not in current_parents:
                    data = self.db[k]
                    if isinstance(data, VersionedRecord):
                        if not isinstance(data.record, DeleteMark):
                            show = True
                            break
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))
            if show:
                for k, p in current_versions.items():
                    data = self.db[k]
                    if isinstance(data, VersionedRecord):
                        yield vuid, k, data
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))

    def list_deleted_versioned(self):
        for vuid in self.db.versions.keys():
            current_versions = self.db.versions[vuid]
            current_parents = self.db.parents[vuid]
            show = False
            for k, p in current_versions.items():
                if k not in current_parents:
                    data = self.db[k]
                    if isinstance(data, VersionedRecord):
                        if isinstance(data.record, DeleteMark):
                            show = True
                            break
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))
            if show:
                for k, p in current_versions.items():
                    data = self.db[k]
                    if isinstance(data, VersionedRecord):
                        yield vuid, k, data
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))

    def list_all_versioned(self):
        for vuid in self.db.versions.keys():
            current_versions = self.db.versions[vuid]
            for k, p in current_versions.items():
                data = self.db[k]
                if isinstance(data, VersionedRecord):
                    yield vuid, k, data
                else:
                    raise ValueError('not versioned record %s in versioned records list: %s' %
                                     (str(k), str(vuid)))

    def list_versioned_type(self, record_type: type):
        for vuid in self.db.versions.keys():
            current_versions = self.db.versions[vuid]
            current_parents = self.db.parents[vuid]
            show = False
            is_record_type = False
            for k, p in current_versions.items():
                if k not in current_parents:
                    data = self.db[k]
                    if isinstance(data, VersionedRecord):
                        if isinstance(data.record, record_type):
                            is_record_type = True
                        if not isinstance(data.record, DeleteMark):
                            show = True
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))
            if show and is_record_type:
                for k, p in current_versions.items():
                    data = self.db[k]
                    if isinstance(data, VersionedRecord):
                        yield vuid, k, data
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))


if __name__ == '__main__':
    raise RuntimeError('This module must not be used independently')
