#!/usr/bin/env python3
"""
Пароль предполагается вводить один раз и хранить все время работы программы.
Пока не будет никаких разных доменов шифрования.
"""


import sys
import inspect  # for command dispatcher
# from PyQt5.QtWidgets import QApplication, QWidget
import uuid
from getpass import getpass
from db import DataBase, PermanentRecord, VersionedRecord, EncryptedRecord, DeleteMark, RevertMark, Note, Task, Category, make_uuid
from datetime import datetime


class MainWindow(object):
    """
    App main window:
        tree in left side
        editor or table or other form in right side
        and splitter between them

    Click on item in Tree show corresponding form in right side
    Changing form in right cause saving data to database
    """
    def __init__(self, db):
        self.db = db


def get_password():
    return getpass(prompt="? ")


def get_test_password():
    return 'kLF9AW8IA0H5WiLcoByZF9H3Yl7FXtBU'


class CMD(object):
    cmd = None

    def __call__(self, *args):
        raise RuntimeError("Abstract command can not be called")


class CMDListNotMarks(CMD):
    cmd = 'lnm'
    description = 'list records that not marks'

    def __call__(self, db: DataBase, *args):
        print("All records:")
        for ruid in db.index.keys():
            if db.marks[ruid] is None:
                data = db[ruid]
                print(ruid, type(data))


class CMDListMarks(CMD):
    cmd = 'lm'
    description = 'list all marks'

    def __call__(self, db: DataBase, *args):
        print("All records:")
        for ruid in db.index.keys():
            if ruid in db.marks and db.marks[ruid] is not None:
                data = db.marks[ruid]
                print(ruid, type(data))


class CMDListAll(CMD):
    cmd = 'la'
    description = 'list all records'

    def __call__(self, db: DataBase, *args):
        print("All records:")
        for ruid in db.index.keys():
            data = db[ruid]
            print(ruid, type(data))


class CMDListPlain(CMD):
    cmd = 'lp'
    description = 'list actual plain (not versioned) records'

    def __call__(self, db: DataBase, *args):
        print("Plain records:")
        for ruid in db.index.keys():
            if db.marks[ruid] is None:
                data = db[ruid]
                if ruid in db.actual and db.actual[ruid] and not isinstance(data, VersionedRecord):
                    print(ruid, type(data))


class CMDListAllPlain(CMD):
    cmd = 'lpa'
    description = 'list all (deleted or not) plain (not versioned) records'

    def __call__(self, db: DataBase, *args):
        print("Plain records:")
        for ruid in db.index.keys():
            if db.marks[ruid] is None:
                data = db[ruid]
                if not isinstance(data, VersionedRecord):
                    print(ruid, type(data))


class CMDListDeleted(CMD):
    cmd = 'ld'
    description = 'list_deleted'

    def __call__(self, db: DataBase, *args):
        print("Deleted records:")
        for ruid in db.index.keys():
            if ruid in db.actual and not db.actual[ruid]:
                data = db[ruid]
                if not isinstance(data, VersionedRecord):
                    print(ruid, type(data))


class CMDListVersioned(CMD):
    cmd = 'lv'
    description = 'list versioned records'

    def __call__(self, db: DataBase, *args):
        print("Versioned records:")
        print('version id')
        print('    record id')
        for vuid in db.versions.keys():
            current_versions = db.versions[vuid]
            current_parents = db.parents[vuid]
            show = False
            for k, p in current_versions.items():
                if k not in current_parents:
                    data = db[k]
                    if isinstance(data, VersionedRecord):
                        if not isinstance(data.record, DeleteMark):
                            show = True
                            break
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))
            if show:
                print(vuid)
                for k, p in current_versions.items():
                    data = db[k]
                    if isinstance(data, VersionedRecord):
                        print('    ', k, type(data.record), p)
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))
            else:
                # print(vuid, 'should not be shown')
                pass


class CMDListDeletedVersioned(CMD):
    cmd = 'lvd'
    description = 'list deleted versioned records'

    def __call__(self, db: DataBase, *args):
        print("Deleted versioned records:")
        print('version id')
        print('    record id')
        for vuid in db.versions.keys():
            current_versions = db.versions[vuid]
            current_parents = db.parents[vuid]
            show = False
            for k, p in current_versions.items():
                if k not in current_parents:
                    data = db[k]
                    if isinstance(data, VersionedRecord):
                        if isinstance(data.record, DeleteMark):
                            show = True
                            break
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))
            if show:
                print(vuid)
                for k, p in current_versions.items():
                    data = db[k]
                    if isinstance(data, VersionedRecord):
                        print('    ', k, type(data.record), p)
                    else:
                        raise ValueError('not versioned record %s in versioned records list: %s' %
                                         (str(k), str(vuid)))
            else:
                # print(vuid, 'should not be shown')
                pass


class CMDListAllVersioned(CMD):
    cmd = 'lva'
    description = 'list all versioned records'

    def __call__(self, db: DataBase, *args):
        print('All versioned records:')
        print('version id')
        print('    record id')
        for vuid in db.versions.keys():
            current_versions = db.versions[vuid]
            print(vuid)
            for k, p in current_versions.items():
                data = db[k]
                if isinstance(data, VersionedRecord):
                    print('    ', k, type(data.record), p)
                else:
                    raise ValueError('not versioned record %s in versioned records list: %s' %
                                     (str(k), str(vuid)))


def list_versioned_type(db: DataBase, record_type):
    for vuid in db.versions.keys():
        current_versions = db.versions[vuid]
        current_parents = db.parents[vuid]
        show = False
        is_record_type = False
        for k, p in current_versions.items():
            if k not in current_parents:
                data = db[k]
                if isinstance(data, VersionedRecord):
                    if isinstance(data.record, record_type):
                        is_record_type = True
                    if not isinstance(data.record, DeleteMark):
                        show = True
                else:
                    raise ValueError('not versioned record %s in versioned records list: %s' %
                                     (str(k), str(vuid)))
        if show and is_record_type:
            print(vuid)
            for k, p in current_versions.items():
                data = db[k]
                if isinstance(data, VersionedRecord):
                    print('    ', k, str(data.record), p)
                else:
                    raise ValueError('not versioned record %s in versioned records list: %s' %
                                     (str(k), str(vuid)))
        else:
            # print(vuid, 'should not be shown')
            pass


class CMDListVersionedNotes(CMD):
    cmd = 'lvn'
    description = 'list versioned notes'

    def __call__(self, db: DataBase, *args):
        print("Versioned notes:")
        print('version id')
        print('    record id')
        list_versioned_type(db, Note)


class CMDListVersionedTasks(CMD):
    cmd = 'lvt'
    description = 'list_versioned_tasks'

    def __call__(self, db: DataBase, *args):
        print("Versioned tasks:")
        print('version id')
        print('    record id')
        list_versioned_type(db, Task)


class CMDListVersionedCategories(CMD):
    cmd = 'lvc'
    description = 'list_versioned_categories'

    def __call__(self, db: DataBase, *args):
        print("Versioned categories:")
        print('version id')
        print('    record id')
        list_versioned_type(db, Category)


class CMDListNotes(CMD):
    cmd = 'lpn'
    description = 'list_notes'

    def __call__(self, db: DataBase, *args):
        print("Plain notes:")
        for ruid in db.index.keys():
            data = db[ruid]
            if ruid in db.actual and db.actual[ruid] and isinstance(data, Note):
                print(ruid, data.title)
        print("")


class CMDListTasks(CMD):
    cmd = 'lpt'
    description = 'list_tasks'

    def __call__(self, db: DataBase, *args):
        print("Plain tasks:")
        for ruid in db.index.keys():
            data = db[ruid]
            if ruid in db.actual and db.actual[ruid] and isinstance(data, Task):
                print(ruid, str(data))
        print("")


class CMDListCategories(CMD):
    cmd = 'lpc'
    description = 'list_categories'

    def __call__(self, db: DataBase, *args):
        print("Plain categories:")
        for ruid in db.index.keys():
            data = db[ruid]
            if ruid in db.actual and db.actual[ruid] and isinstance(data, Category):
                print(ruid, str(data))
        print("")


class CMDListNotesInCategory(CMD):
    cmd = 'lpnc'
    description = 'list_notes_in_category <record uid of category>'

    def __call__(self, db: DataBase, *args):
        category_ruid = uuid.UUID(args[0])
        if category_ruid not in db:
            raise ValueError('category ruid %s not in DB' % category_ruid)
        category = db[category_ruid]
        if not isinstance(category, Category):
            raise ValueError('%s not a category' % category_ruid)

        print("Notes in category %s:" % str(category))
        for ruid in db.index.keys():
            data = db[ruid]
            if ruid in db.actual and db.actual[ruid] and isinstance(data, Note):
                if category_ruid in data.categories:
                    print(ruid, data.title)
        print("")


class CMDListTasksInCategory(CMD):
    cmd = 'lptc'
    description = 'list_tasks_in_category'

    def __call__(self, db: DataBase, *args):
        category_ruid = uuid.UUID(args[0])
        if category_ruid not in db:
            raise ValueError('category ruid %s not in DB' % category_ruid)
        category = db[category_ruid]
        if not isinstance(category, Category):
            raise ValueError('%s not a category' % category_ruid)

        print("Tasks in category %s:" % str(category))
        for ruid in db.index.keys():
            data = db[ruid]
            if ruid in db.actual and db.actual[ruid] and isinstance(data, Task):
                if category_ruid in data.categories:
                    print(ruid, str(data))
        print("")


def list_versioned_type_in_category(db: DataBase, record_type: type, category_ruid: uuid.UUID):
    # category_ruid = uuid.UUID(args[0])
    if category_ruid not in db:
        raise ValueError('category ruid %s not in DB' % category_ruid)
    category = db[category_ruid]
    if not isinstance(category, Category):
        raise ValueError('%s not a category' % category_ruid)

    print("Versioned %ss in category %s:" % (record_type.__name__, str(category)))
    print('version id')
    print('    record id')
    for vuid in db.versions.keys():
        current_versions = db.versions[vuid]
        current_parents = db.parents[vuid]
        show = False
        is_record_type = False
        for k, p in current_versions.items():
            if k not in current_parents:
                data = db[k]
                if isinstance(data, VersionedRecord):
                    if isinstance(data.record, record_type):
                        is_record_type = True
                    if not isinstance(data.record, DeleteMark):
                        show = True
                else:
                    raise ValueError('not versioned record %s in versioned records list: %s' %
                                     (str(k), str(vuid)))
        if show and is_record_type:
            print(vuid)
            for k, p in current_versions.items():
                data = db[k]
                if isinstance(data, VersionedRecord):
                    print('    ', k, str(data.record), p)
                else:
                    raise ValueError('not versioned record %s in versioned records list: %s' %
                                     (str(k), str(vuid)))
        else:
            # print(vuid, 'should not be shown')
            pass


class CMDListVersionedNotesInCategory(CMD):
    cmd = 'lvnc'
    description = 'list versioned notes in category <category vuid>'

    def __call__(self, db: DataBase, *args):
        list_versioned_type_in_category(db, Note, uuid.UUID(args[0]))


class CMDListVersionedTasksInCategory(CMD):
    cmd = 'lvtc'
    description = 'list_versioned_tasks in category <category vuid>'

    def __call__(self, db: DataBase, *args):
        list_versioned_type_in_category(db, Task, uuid.UUID(args[0]))


class CMDAddNote(CMD):
    cmd = 'an'
    description = 'add_note'

    def __call__(self, db: DataBase, *args):
        if len(args) != 2:
            raise ValueError("%s needs 2 arguments %d given" % (self.__class__.description, len(args)))
        note_ruid = db.append(PermanentRecord(Note(args[0], args[1])))
        print(note_ruid)


class CMDAddCategory(CMD):
    cmd = 'ac'
    description = 'add_category'

    def __call__(self, db: DataBase, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument %d given" % (self.__class__.description, len(args)))
        category_ruid = db.append(PermanentRecord(Category(args[0])))
        print(category_ruid)


class CMDAddTask(CMD):
    cmd = 'at'
    description = 'add_task'

    def __call__(self, db: DataBase, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument %d given" % (self.__class__.description, len(args)))
        task_ruid = db.append(PermanentRecord(Task(args[0])))
        print(task_ruid)


class CMDAddVersionedNote(CMD):
    cmd = 'avn'
    description = 'Add versioned note.     Usage: avn [version uid] <title> <text> [parent record uid ...]'

    def __call__(self, db: DataBase, *args):
        if len(args) == 2:
            vuid = make_uuid()
            note_ruid = db.append(PermanentRecord(VersionedRecord(Note(args[0], args[1]), datetime.now(), vuid)))
        elif len(args) >= 3:
            vuid = uuid.UUID(args[0])
            note_ruid = db.append(PermanentRecord(VersionedRecord(Note(args[1], args[2]), datetime.now(),
                                                                  vuid,
                                                                  *[uuid.UUID(parent) for parent in args[3:]])))
        else:
            raise ValueError("%s needs 2 or 3 or more arguments %d given" % (self.__class__.description, len(args)))
        print(note_ruid)


class CMDAddVersionedCategory(CMD):
    cmd = 'avc'
    description = 'Add versioned category. Usage: avc [version uid] <title> [parent record uid ...]'

    def __call__(self, db: DataBase, *args):
        if len(args) == 1:
            vuid = make_uuid()
            note_ruid = db.append(PermanentRecord(VersionedRecord(Category(args[0]), datetime.now(), vuid)))
        elif len(args) >= 2:
            vuid = uuid.UUID(args[0])
            note_ruid = db.append(PermanentRecord(VersionedRecord(Category(args[1]), datetime.now(),
                                                                  vuid,
                                                                  *[uuid.UUID(parent) for parent in args[2:]])))
        else:
            raise ValueError("%s needs 1 or 2 or more arguments %d given" % (self.__class__.description, len(args)))
        print(note_ruid)


class CMDAddVersionedTask(CMD):
    cmd = 'avt'
    description = 'Add versioned task.     Usage: avt [version uid] <title> [parent record uid ...]'

    def __call__(self, db: DataBase, *args):
        if len(args) == 1:
            vuid = make_uuid()
            note_ruid = db.append(PermanentRecord(VersionedRecord(Task(args[0]), datetime.now(), vuid)))
        elif len(args) >= 2:
            vuid = uuid.UUID(args[0])
            note_ruid = db.append(PermanentRecord(VersionedRecord(Task(args[1]), datetime.now(),
                                                                  vuid,
                                                                  *[uuid.UUID(parent) for parent in args[2:]])))
        else:
            raise ValueError("%s needs 1 or 2 or more arguments %d given" % (self.__class__.description, len(args)))
        print(note_ruid)


class CMDDeleteRecord(CMD):
    cmd = 'd'
    description = 'Delete record. Usage: d <uid>'

    def __call__(self, db: DataBase, *args):
        """
        Add DeleteMark to db 
        """
        if len(args) != 1:
            raise ValueError("%s needs only one argument but %d given" % (self.__class__.description, len(args)))
        delete_mark_uid = db.append(PermanentRecord(DeleteMark(uuid.UUID(args[0]))))
        print(delete_mark_uid)


class CMDRevertRecord(CMD):
    cmd = 'r'
    description = 'Revert record. Usage: r <uid>'

    def __call__(self, db: DataBase, *args):
        """
        Add RevertMark to db
        """
        if len(args) != 1:
            raise ValueError("%s needs only one argument but %d given" % (self.__class__.description, len(args)))
        revert_mark_uid = db.append(PermanentRecord(RevertMark(uuid.UUID(args[0]))))
        print(revert_mark_uid)


class CMDDeleteVersionedRecord(CMD):
    cmd = 'dv'
    description = 'Delete versioned record: Usage: dv <version uid> <record uid>'

    def __call__(self, db: DataBase, *args):
        if len(args) == 2:
            vuid = uuid.UUID(args[0])
            ruid = uuid.UUID(args[1])

            if ruid not in db.index.keys():
                raise ValueError('record uid %s not in DB' % ruid)
            if vuid not in db.versions:
                raise ValueError('version uid %s not in version index' % vuid)

            task_record = db[ruid]
            if not isinstance(task_record, VersionedRecord):
                raise ValueError('specified record %s not a VersionedRecord' % ruid)
            if not isinstance(task_record.record, DeleteMark):
                delete_mark_uid = db.append(PermanentRecord(VersionedRecord(DeleteMark(ruid), datetime.now(),
                                                                            vuid, ruid)))
                print(delete_mark_uid)
            else:
                print("%s %s already deleted" % (str(vuid), str(ruid)))
        else:
            raise ValueError("%s needs 2 arguments %d given" % (self.__class__.description, len(args)))


class CMDRevertVersionedRecord(CMD):
    cmd = 'rv'
    description = 'Revert versioned record: Usage: rv <version uid> <record uid>'

    def __call__(self, db: DataBase, *args):
        if len(args) == 2:
            vuid = uuid.UUID(args[0])
            ruid = uuid.UUID(args[1])

            if ruid not in db.index.keys():
                raise ValueError('record uid %s not in DB' % ruid)
            if vuid not in db.versions:
                raise ValueError('version uid %s not in version index' % vuid)

            task_record = db[ruid]
            if not isinstance(task_record, VersionedRecord):
                raise ValueError('specified record %s not a VersionedRecord' % ruid)
            if isinstance(task_record.record, DeleteMark):
                delete_mark_uid = db.append(PermanentRecord(VersionedRecord(RevertMark(ruid), datetime.now(),
                                                                            vuid, ruid)))
                print(delete_mark_uid)
            else:
                print("%s %s not deleted" % (str(vuid), str(ruid)))
        else:
            raise ValueError("%s needs 2 arguments %d given" % (self.__class__.description, len(args)))


class CMDDoneTask(CMD):
    cmd = 'dt'
    description = 'Done task. Usage: dt <uid>'

    def __call__(self, db: DataBase, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument but %d given" % (self.__class__.description, len(args)))
        ruid = uuid.UUID(args[0])
        if ruid not in db.index.keys():
            raise ValueError('uid %s not in database' % ruid)
        task_record = db[ruid]
        if not isinstance(task_record, Task):
            raise ValueError('Records with uid %s is not a task' % ruid)
        if not task_record.done:
            task_record.done = True
            print(task_record)
            db.append(PermanentRecord(DeleteMark(ruid)))
            db.append(PermanentRecord(task_record))


class CMDUnDoneTask(CMD):
    cmd = 'udt'
    description = 'Undone task. Usage: udt <uid>'

    def __call__(self, db: DataBase, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument but %d given" % (self.__class__.description, len(args)))
        ruid = uuid.UUID(args[0])
        if ruid not in db.index.keys():
            raise ValueError('uid %s not in database' % ruid)
        task_record = db[ruid]
        if not isinstance(task_record, Task):
            raise ValueError('Records with uid %s is not a task' % ruid)
        if task_record.done:
            task_record.done = False
            db.append(PermanentRecord(DeleteMark(ruid)))
            db.append(PermanentRecord(task_record))


class CMDDoneVersionedTask(CMD):
    cmd = 'dvt'
    description = 'done_task'

    def __call__(self, db: DataBase, *args):
        if len(args) != 2:
            raise ValueError("%s needs 2 argument but %d given" % (self.__class__.description, len(args)))
        vuid = uuid.UUID(args[0])
        ruid = uuid.UUID(args[1])

        if ruid not in db.versions:
            raise ValueError('uid %s not in database' % ruid)
        task_record = db[vuid]
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
            new_uid = db.append(PermanentRecord(VersionedRecord(task, datetime.now(),
                                                                ruid, vuid)))
            print(new_uid)
        else:
            print('vuid already done')


class CMDUnDoneVersionedTask(CMD):
    cmd = 'udvt'
    description = 'undone_task'

    def __call__(self, db: DataBase, *args):
        if len(args) != 2:
            raise ValueError("%s needs 2 argument but %d given" % (self.__class__.description, len(args)))
        vuid = uuid.UUID(args[0])
        ruid = uuid.UUID(args[1])

        if ruid not in db.index.keys():
            raise ValueError('uid %s not in database' % ruid)
        if vuid not in db.versions:
            raise ValueError('uid %s not version' % vuid)
        task_record = db[ruid]
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
            new_uid = db.append(PermanentRecord(VersionedRecord(task, datetime.now(),
                                                                ruid, vuid)))
            print(new_uid)
        else:
            print('vuid already undone')


class Dispatcher(object):
    class Command(object):
        def __init__(self, description, command):
            self.description = description
            self.command = command

    def __init__(self, base_class):
        self.commands = {}
        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj) and issubclass(obj, base_class) and obj is not CMD:
                if obj.cmd in self.commands:
                    raise ValueError("Duplicate command %s" % obj.cmd)
                self.commands[obj.cmd] = Dispatcher.Command(obj.description, obj())

    def help(self, file=sys.stderr):
        for cmd_name in sorted(self.commands.keys()):
            cmd = self.commands[cmd_name]
            print('   %3s --- %-25s' % (cmd_name, cmd.description), file=file)

    def __call__(self, command_name, *args):
        if command_name in self.commands:
            cmd = self.commands[command_name]
            return cmd.command(*args)
        else:
            raise ValueError('Unknown command "%s"' % str(command_name))


def usage(descriptions: Dispatcher):
    print('usage: pim.py command [arguments...]', file=sys.stderr)
    descriptions.help()


def main_console():
    dispatcher = Dispatcher(CMD)
    if len(sys.argv) < 2:
        usage(dispatcher)
    else:
        db = DataBase('test.data', get_test_password)
        try:
            dispatcher(sys.argv[1], db, *sys.argv[2:])
        except ValueError as ex:
            print(ex)
            usage(dispatcher)


if __name__ == '__main__':
    main_console()
