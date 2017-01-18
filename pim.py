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
from typing import Iterable

from db import PIMDB, Note, Task, Category


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

    def __call__(self, db: PIMDB, *args):
        print("All records:")
        for ruid, data in db.list_not_marks():
            print(ruid, type(data))


class CMDListMarks(CMD):
    cmd = 'lm'
    description = 'list all marks'

    def __call__(self, db: PIMDB, *args):
        print("All records:")
        for ruid, data in db.list_marks():
            print(ruid, type(data))


class CMDListAll(CMD):
    cmd = 'la'
    description = 'list all records'

    def __call__(self, db: PIMDB, *args):
        print("All records:")
        for ruid, data in db.list_all():
            print(ruid, type(data))


class CMDListPlain(CMD):
    cmd = 'lp'
    description = 'list actual plain (not versioned) records'

    def __call__(self, db: PIMDB, *args):
        print("Plain records:")
        for ruid, data in db.list_plain():
            print(ruid, type(data))


class CMDListAllPlain(CMD):
    cmd = 'lpa'
    description = 'list all (deleted or not) plain (not versioned) records'

    def __call__(self, db: PIMDB, *args):
        print("Plain records:")
        for ruid, data in db.list_plain():
            print(ruid, type(data))


class CMDListDeleted(CMD):
    cmd = 'ld'
    description = 'list_deleted'

    def __call__(self, db: PIMDB, *args):
        print("Deleted records:")
        for ruid, data in db.list_plain():
            if not db.is_plain_deleted(ruid):
                print(ruid, type(data))


def list_versioned_records(generator: Iterable):
    v = None
    for vuid, ruid, data in generator:
        if vuid != v:
            v = vuid
            print(vuid)
        print('    ', ruid, type(data.record))


class CMDListVersioned(CMD):
    cmd = 'lv'
    description = 'list versioned records'

    def __call__(self, db: PIMDB, *args):
        print("Versioned records:")
        print('version id, record id')
        list_versioned_records(db.list_versioned())


class CMDListDeletedVersioned(CMD):
    cmd = 'lvd'
    description = 'list deleted versioned records'

    def __call__(self, db: PIMDB, *args):
        print("Deleted versioned records:")
        print('version id')
        print('    record id')
        list_versioned_records(db.list_deleted_versioned())


class CMDListAllVersioned(CMD):
    cmd = 'lva'
    description = 'list all versioned records'

    def __call__(self, db: PIMDB, *args):
        print('All versioned records:')
        print('version id')
        print('    record id')
        list_versioned_records(db.list_all_versioned())


class CMDListVersionedNotes(CMD):
    cmd = 'lvn'
    description = 'list versioned notes'

    def __call__(self, db: PIMDB, *args):
        print("Versioned notes:")
        print('version id')
        print('    record id')
        list_versioned_records(db.list_versioned_type(Note))


class CMDListVersionedTasks(CMD):
    cmd = 'lvt'
    description = 'list_versioned_tasks'

    def __call__(self, db: PIMDB, *args):
        print("Versioned tasks:")
        print('version id')
        print('    record id')
        list_versioned_records(db.list_versioned_type(Task))


class CMDListVersionedCategories(CMD):
    cmd = 'lvc'
    description = 'list_versioned_categories'

    def __call__(self, db: PIMDB, *args):
        print("Versioned categories:")
        print('version id')
        print('    record id')
        list_versioned_records(db.list_versioned_type(Category))


class CMDListNotes(CMD):
    cmd = 'lpn'
    description = 'list_notes'

    def __call__(self, db: PIMDB, *args):
        print("Plain notes:")
        for ruid, data in db.list_plain():
            if db.is_plain_actual(ruid) and isinstance(data, Note):
                print(ruid, data.title)
        print("")


class CMDListTasks(CMD):
    cmd = 'lpt'
    description = 'list_tasks'

    def __call__(self, db: PIMDB, *args):
        print("Plain tasks:")
        for ruid, data in db.list_plain():
            if db.is_plain_actual(ruid) and isinstance(data, Task):
                print(ruid, data.title)
        print("")


class CMDListCategories(CMD):
    cmd = 'lpc'
    description = 'list_categories'

    def __call__(self, db: PIMDB, *args):
        print("Plain categories:")
        for ruid, data in db.list_plain():
            if db.is_plain_actual(ruid) and isinstance(data, Category):
                print(ruid, data.title)
        print("")


class CMDListNotesInCategory(CMD):
    cmd = 'lpnc'
    description = 'list_notes_in_category <record uid of category>'

    def __call__(self, db: PIMDB, *args):
        category_ruid = uuid.UUID(args[0])
        if category_ruid not in db:
            raise ValueError('category ruid %s not in DB' % category_ruid)
        category = db[category_ruid]
        if not isinstance(category, Category):
            raise ValueError('%s not a category' % category_ruid)

        print("Notes in category %s:" % str(category))
        for ruid, data in db.list_plain():
            if db.is_plain_actual(ruid) and isinstance(data, Note):
                if category_ruid in data.categories:
                    print(ruid, data.title)
        print("")


class CMDListTasksInCategory(CMD):
    cmd = 'lptc'
    description = 'list_tasks_in_category'

    def __call__(self, db: PIMDB, *args):
        category_ruid = uuid.UUID(args[0])
        if category_ruid not in db:
            raise ValueError('category ruid %s not in DB' % category_ruid)
        category = db[category_ruid]
        if not isinstance(category, Category):
            raise ValueError('%s not a category' % category_ruid)

        print("Tasks in category %s:" % str(category))
        for ruid, data in db.list_plain():
            if db.is_plain_actual(ruid) and isinstance(data, Note):
                if category_ruid in data.categories:
                    print(ruid, data.title)
        print("")


def list_versioned_records_in_category(generator: Iterable, category_uid: uuid.UUID):
    v = None
    for vuid, ruid, data in generator:
        if category_uid in data.record.categories:
            if vuid != v:
                v = vuid
                print(vuid)
            print('    ', ruid, type(data.record))


class CMDListVersionedNotesInCategory(CMD):
    cmd = 'lvnc'
    description = 'list versioned notes in category <category vuid>'

    def __call__(self, db: PIMDB, *args):
        list_versioned_records_in_category(db.list_versioned_type(Note), uuid.UUID(args[0]))


class CMDListVersionedTasksInCategory(CMD):
    cmd = 'lvtc'
    description = 'list_versioned_tasks in category <category vuid>'

    def __call__(self, db: PIMDB, *args):
        list_versioned_records_in_category(db.list_versioned_type(Task), uuid.UUID(args[0]))


class CMDAddNote(CMD):
    cmd = 'an'
    description = 'add_note'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 2:
            raise ValueError("%s needs 2 arguments %d given" % (self.__class__.description, len(args)))
        print(db.add_plain_record(Note(args[0], args[1])))


class CMDAddCategory(CMD):
    cmd = 'ac'
    description = 'add_category'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument %d given" % (self.__class__.description, len(args)))
        print(db.add_plain_record(Category(args[0])))


class CMDAddTask(CMD):
    cmd = 'at'
    description = 'add_task'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument %d given" % (self.__class__.description, len(args)))
        print(db.add_plain_record(Task(args[0])))


class CMDAddVersionedNote(CMD):
    cmd = 'avn'
    description = 'Add versioned note.     Usage: avn [version uid] <title> <text> [parent record uid ...]'

    def __call__(self, db: PIMDB, *args):
        if len(args) == 2:
            new_ruid = db.add_versioned_record(Note(args[0], args[1]))
        elif len(args) >= 3:
            vuid = uuid.UUID(args[0])
            new_ruid = db.add_versioned_record(Note(args[1], args[2]), vuid,
                                               *[uuid.UUID(parent) for parent in args[3:]])
        else:
            raise ValueError("%s needs 2 or 3 or more arguments %d given" % (self.__class__.description, len(args)))
        print(new_ruid)


class CMDAddVersionedCategory(CMD):
    cmd = 'avc'
    description = 'Add versioned category. Usage: avc [version uid] <title> [parent record uid ...]'

    def __call__(self, db: PIMDB, *args):
        if len(args) == 1:
            new_ruid = db.add_versioned_record(Category(args[0]))
        elif len(args) >= 2:
            vuid = uuid.UUID(args[0])
            new_ruid = db.add_versioned_record(Category(args[1]), vuid, *[uuid.UUID(parent) for parent in args[2:]])
        else:
            raise ValueError("%s needs 1 or 2 or more arguments %d given" % (self.__class__.description, len(args)))
        print(new_ruid)


class CMDAddVersionedTask(CMD):
    cmd = 'avt'
    description = 'Add versioned task.     Usage: avt [version uid] <title> [parent record uid ...]'

    def __call__(self, db: PIMDB, *args):
        if len(args) == 1:
            new_ruid = db.add_versioned_record(Task(args[0]))
        elif len(args) >= 2:
            vuid = uuid.UUID(args[0])
            new_ruid = db.add_versioned_record(Task(args[1]), vuid, *[uuid.UUID(parent) for parent in args[2:]])
        else:
            raise ValueError("%s needs 1 or 2 or more arguments %d given" % (self.__class__.description, len(args)))
        print(new_ruid)


# Encrypted versions of adding commands

class CMDAddEncryptedNote(CMD):
    cmd = 'aen'
    description = 'add encrypted note'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 2:
            raise ValueError("%s needs 2 arguments %d given" % (self.__class__.description, len(args)))
        print(db.add_encrypted_plain_record(Note(args[0], args[1]), ))


class CMDAddEncryptedCategory(CMD):
    cmd = 'aec'
    description = 'add encrypted category'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument %d given" % (self.__class__.description, len(args)))
        print(db.add_encrypted_plain_record(Category(args[0])))


class CMDAddEncryptedTask(CMD):
    cmd = 'aet'
    description = 'add encrypted task'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument %d given" % (self.__class__.description, len(args)))
        print(db.add_encrypted_plain_record(Task(args[0])))


class CMDAddEncryptedVersionedNote(CMD):
    cmd = 'aevn'
    description = 'Add encrypted versioned note.     Usage: avn [version uid] <title> <text> [parent record uid ...]'

    def __call__(self, db: PIMDB, *args):
        if len(args) == 2:
            new_ruid = db.add_encrypted_versioned_record(Note(args[0], args[1]))
        elif len(args) >= 3:
            vuid = uuid.UUID(args[0])
            new_ruid = db.add_encrypted_versioned_record(Note(args[1], args[2]), vuid,
                                                         *[uuid.UUID(parent) for parent in args[3:]])
        else:
            raise ValueError("%s needs 2 or 3 or more arguments %d given" % (self.__class__.description, len(args)))
        print(new_ruid)


class CMDAddEncryptedVersionedCategory(CMD):
    cmd = 'aevc'
    description = 'Add encrypted versioned category. Usage: avc [version uid] <title> [parent record uid ...]'

    def __call__(self, db: PIMDB, *args):
        if len(args) == 1:
            new_ruid = db.add_encrypted_versioned_record(Category(args[0]))
        elif len(args) >= 2:
            vuid = uuid.UUID(args[0])
            new_ruid = db.add_encrypted_versioned_record(Category(args[1]), vuid,
                                                         *[uuid.UUID(parent) for parent in args[2:]])
        else:
            raise ValueError("%s needs 1 or 2 or more arguments %d given" % (self.__class__.description, len(args)))
        print(new_ruid)


class CMDAddEncryptedVersionedTask(CMD):
    cmd = 'aevt'
    description = 'Add encrypted versioned task.     Usage: avt [version uid] <title> [parent record uid ...]'

    def __call__(self, db: PIMDB, *args):
        if len(args) == 1:
            new_ruid = db.add_encrypted_versioned_record(Task(args[0]))
        elif len(args) >= 2:
            vuid = uuid.UUID(args[0])
            new_ruid = db.add_encrypted_versioned_record(Task(args[1]), vuid,
                                                         *[uuid.UUID(parent) for parent in args[2:]])
        else:
            raise ValueError("%s needs 1 or 2 or more arguments %d given" % (self.__class__.description, len(args)))
        print(new_ruid)


# Delete commands

class CMDDeleteRecord(CMD):
    cmd = 'd'
    description = 'Delete record. Usage: d <uid>'

    def __call__(self, db: PIMDB, *args):
        """
        Add DeleteMark to db 
        """
        if len(args) != 1:
            raise ValueError("%s needs only one argument but %d given" % (self.__class__.description, len(args)))
        print(db.delete_plain_record(uuid.UUID(args[0])))


class CMDRevertRecord(CMD):
    cmd = 'r'
    description = 'Revert record. Usage: r <uid>'

    def __call__(self, db: PIMDB, *args):
        """
        Add RevertMark to db
        """
        if len(args) != 1:
            raise ValueError("%s needs only one argument but %d given" % (self.__class__.description, len(args)))
        print(db.revert_plain_record(uuid.UUID(args[0])))


class CMDDeleteVersionedRecord(CMD):
    cmd = 'dv'
    description = 'Delete versioned record: Usage: dv <version uid> <record uid>'

    def __call__(self, db: PIMDB, *args):
        if len(args) == 2:
            vuid = uuid.UUID(args[0])
            ruid = uuid.UUID(args[1])

            print(db.delete_versioned_record(vuid, ruid))
        else:
            raise ValueError("%s needs 2 arguments %d given" % (self.__class__.description, len(args)))


class CMDRevertVersionedRecord(CMD):
    cmd = 'rv'
    description = 'Revert versioned record: Usage: rv <version uid> <record uid>'

    def __call__(self, db: PIMDB, *args):
        if len(args) == 2:
            vuid = uuid.UUID(args[0])
            ruid = uuid.UUID(args[1])

            delete_mark_uid = db.delete_versioned_record(vuid, ruid)
            if delete_mark_uid is not None:
                print(delete_mark_uid)
            else:
                print("%s %s not deleted" % (str(vuid), str(ruid)))
        else:
            raise ValueError("%s needs 2 arguments %d given" % (self.__class__.description, len(args)))


class CMDDoneTask(CMD):
    cmd = 'dt'
    description = 'Done task. Usage: dt <uid>'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument but %d given" % (self.__class__.description, len(args)))
        ruid = uuid.UUID(args[0])
        print(db.done_plain_task(ruid))


class CMDUnDoneTask(CMD):
    cmd = 'udt'
    description = 'Undone task. Usage: udt <uid>'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 1:
            raise ValueError("%s needs 1 argument but %d given" % (self.__class__.description, len(args)))
        ruid = uuid.UUID(args[0])
        print(db.undone_plain_task(ruid))


class CMDDoneVersionedTask(CMD):
    cmd = 'dvt'
    description = 'done_task'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 2:
            raise ValueError("%s needs 2 argument but %d given" % (self.__class__.description, len(args)))
        vuid = uuid.UUID(args[0])
        ruid = uuid.UUID(args[1])

        done_ruid = db.done_versioned_task(vuid, ruid)
        if done_ruid is not None:
            print(done_ruid)
        else:
            print('vuid already done')


class CMDUnDoneVersionedTask(CMD):
    cmd = 'udvt'
    description = 'undone_task'

    def __call__(self, db: PIMDB, *args):
        if len(args) != 2:
            raise ValueError("%s needs 2 argument but %d given" % (self.__class__.description, len(args)))
        vuid = uuid.UUID(args[0])
        ruid = uuid.UUID(args[1])

        undone_ruid = db.undone_versioned_task(vuid, ruid)
        if undone_ruid is not None:
            print(undone_ruid)
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
        db = PIMDB('test.data', get_test_password)
        try:
            dispatcher(sys.argv[1], db, *sys.argv[2:])
        except ValueError as ex:
            print(ex)
            usage(dispatcher)


if __name__ == '__main__':
    main_console()
