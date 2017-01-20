import unittest
from db import *
import os


class TestPIM(unittest.TestCase):
    @staticmethod
    def _get_test_password():
        return 'kLF9AW8IA0H5WiLcoByZF9H3Yl7FXtBU'

    def test_db_one_note(self):
        os.unlink('test_db.data')
        db = DataBase('test_db.data', self._get_test_password)

        n1 = db.append(PermanentRecord(Note("Note title 1", "Note text 1\nNote text 1")))
        self.assertIsInstance(n1, uuid.UUID)
        # print(db[n1])

    def test_marks(self):
        dm = DeleteMark(make_uuid())
        rm = RevertMark(make_uuid())

        self.assertIsInstance(dm, Record)
        self.assertIsInstance(rm, Record)

        self.assertIsInstance(str(dm), str)
        self.assertIsInstance(str(rm), str)

    def test_concrete_records(self):
        note = Note("title", "text")
        task = Task("title")
        category = Category("title")
        url = BookmarkURL("title", "url")
        project = Project("title", "description")
        target = Target("title", "description")
        password = Password("title", "login", "Password")

        self.assertEquals(note.title, "title")
        self.assertEquals(task.title, "title")
        self.assertEquals(category.title, "title")
        self.assertEquals(url.title, "title")
        self.assertEquals(project.title, "title")
        self.assertEquals(target.title, "title")
        self.assertEquals(password.service, "service")

        self.assertIsInstance(str(note), str)
        self.assertIsInstance(str(task), str)
        self.assertIsInstance(str(category), str)
        self.assertIsInstance(str(url), str)
        self.assertIsInstance(str(project), str)
        self.assertIsInstance(str(target), str)
        self.assertIsInstance(str(password), str)

        note2 = Note("title", "text", categories=[category, ])
        self.assertIsInstance(note2.categories, list)

        task2 = Task("title", categories=[category, ])
        self.assertIsInstance(task2.categories, list)

    def test_db(self):
        os.unlink('test_db.data')
        db = DataBase('test_db.data', self._get_test_password)

        n1 = db.append(PermanentRecord(Note("Note title 1", "Note text 1\nNote text 1")))
        n2 = db.append(PermanentRecord(Note("Note title 2", "Note text 2\nNote text 2")))
        n3 = db.append(PermanentRecord(Note("Note title 3", "Note text 3\nNote text 3")))

        t1 = db.append(PermanentRecord(Task("Task 1")))
        t2 = db.append(PermanentRecord(Task("Task 2")))
        t3 = db.append(PermanentRecord(Task("Task 3")))
        t4 = db.append(PermanentRecord(Task("Task 4")))

        self.assertIsInstance(n1, uuid.UUID)
        self.assertIsInstance(n2, uuid.UUID)
        self.assertIsInstance(n3, uuid.UUID)

        self.assertIsInstance(t1, uuid.UUID)
        self.assertIsInstance(t2, uuid.UUID)
        self.assertIsInstance(t3, uuid.UUID)
        self.assertIsInstance(t4, uuid.UUID)

        self.assertIsInstance(db[n1], Note)
        self.assertIsInstance(db[n2], Note)
        self.assertIsInstance(db[n3], Note)

        self.assertIsInstance(db[t1], Task)
        self.assertIsInstance(db[t2], Task)
        self.assertIsInstance(db[t3], Task)
        self.assertIsInstance(db[t4], Task)

        def assert_note_title(r: Record, title: str):
            assert isinstance(r, Note)
            self.assertEqual(r.title, title)

        def assert_task_title(r: Record, title: str):
            assert isinstance(r, Task)
            self.assertEqual(r.title, title)

        assert_note_title(db[n1], "Note title 1")
        assert_note_title(db[n2], "Note title 2")
        assert_note_title(db[n3], "Note title 3")

        assert_task_title(db[t1], Task("Task 1").title)
        assert_task_title(db[t2], Task("Task 2").title)
        assert_task_title(db[t3], Task("Task 3").title)
        assert_task_title(db[t4], Task("Task 4").title)

        n1 = db.append(EncryptedRecord(Note("E Note title 1", "Note text 1\nNote text 1"), self._get_test_password))
        n2 = db.append(EncryptedRecord(Note("E Note title 2", "Note text 2\nNote text 2"), self._get_test_password))
        n3 = db.append(EncryptedRecord(Note("E Note title 3", "Note text 3\nNote text 3"), self._get_test_password))

        t1 = db.append(EncryptedRecord(Task("E Task 1"), self._get_test_password))
        t2 = db.append(EncryptedRecord(Task("E Task 2"), self._get_test_password))
        t3 = db.append(EncryptedRecord(Task("E Task 3"), self._get_test_password))
        t4 = db.append(EncryptedRecord(Task("E Task 4"), self._get_test_password))

        self.assertIsInstance(n1, uuid.UUID)
        self.assertIsInstance(n2, uuid.UUID)
        self.assertIsInstance(n3, uuid.UUID)

        self.assertIsInstance(t1, uuid.UUID)
        self.assertIsInstance(t2, uuid.UUID)
        self.assertIsInstance(t3, uuid.UUID)
        self.assertIsInstance(t4, uuid.UUID)

        self.assertIsInstance(db[n1], Note)
        self.assertIsInstance(db[n2], Note)
        self.assertIsInstance(db[n3], Note)

        self.assertIsInstance(db[t1], Task)
        self.assertIsInstance(db[t2], Task)
        self.assertIsInstance(db[t3], Task)
        self.assertIsInstance(db[t4], Task)

        assert_note_title(db[n1], "E Note title 1")
        assert_note_title(db[n2], "E Note title 2")
        assert_note_title(db[n3], "E Note title 3")

        assert_task_title(db[t1], Task("E Task 1").title)
        assert_task_title(db[t2], Task("E Task 2").title)
        assert_task_title(db[t3], Task("E Task 3").title)
        assert_task_title(db[t4], Task("E Task 4").title)

        # Now test temporary records
        db2 = DataBase('test_db.data', self._get_test_password)

        n1 = db2.append(TemporaryRecord(Note("Note title 1", "Note text 1\nNote text 1")))
        n2 = db2.append(TemporaryRecord(Note("Note title 2", "Note text 2\nNote text 2")))
        n3 = db2.append(TemporaryRecord(Note("Note title 3", "Note text 3\nNote text 3")))

        t1 = db2.append(TemporaryRecord(Task("Task 1")))
        t2 = db2.append(TemporaryRecord(Task("Task 2")))
        t3 = db2.append(TemporaryRecord(Task("Task 3")))
        t4 = db2.append(TemporaryRecord(Task("Task 4")))

        self.assertIsInstance(n1, uuid.UUID)
        self.assertIsInstance(n2, uuid.UUID)
        self.assertIsInstance(n3, uuid.UUID)

        self.assertIsInstance(t1, uuid.UUID)
        self.assertIsInstance(t2, uuid.UUID)
        self.assertIsInstance(t3, uuid.UUID)
        self.assertIsInstance(t4, uuid.UUID)

        self.assertIsInstance(db[n1], Note)
        self.assertIsInstance(db[n2], Note)
        self.assertIsInstance(db[n3], Note)

        self.assertIsInstance(db[t1], Task)
        self.assertIsInstance(db[t2], Task)
        self.assertIsInstance(db[t3], Task)
        self.assertIsInstance(db[t4], Task)

        assert_note_title(db[n1], "Note title 1")
        assert_note_title(db[n2], "Note title 2")
        assert_note_title(db[n3], "Note title 3")

        assert_task_title(db[t1], Task("Task 1").title)
        assert_task_title(db[t2], Task("Task 2").title)
        assert_task_title(db[t3], Task("Task 3").title)
        assert_task_title(db[t4], Task("Task 4").title)

    def test_db_versioned(self):
        os.unlink('test_db.data')
        db = DataBase('test_db.data', self._get_test_password)

        n1 = db.append(PermanentRecord(Note("Note title 1", "Note text 1\nNote text 1")))
        n2 = db.append(PermanentRecord(Note("Note title 2", "Note text 2\nNote text 2")))
        n3 = db.append(PermanentRecord(Note("Note title 3", "Note text 3\nNote text 3")))

        t1 = db.append(PermanentRecord(Task("Task 1")))
        t2 = db.append(PermanentRecord(Task("Task 2")))
        t3 = db.append(PermanentRecord(Task("Task 3")))
        t4 = db.append(PermanentRecord(Task("Task 4")))

        vuid1 = make_uuid()
        vn1 = db.append(PermanentRecord(VersionedRecord(Note("Note title 1", "Note text 1\nNote text 1"),
                                                        datetime.now(),
                                                        vuid1)))
        self.assertIsInstance(vn1, uuid.UUID)

        vn2 = db.append(PermanentRecord(VersionedRecord(Note("Note title 2", "Note text 1\nNote text 2"),
                                                        datetime.now(),
                                                        vuid1,
                                                        vn1)))
        self.assertIsInstance(vn2, uuid.UUID)

        vn3 = db.append(PermanentRecord(VersionedRecord(Note("Note title 3", "Note text 1\nNote text 3"),
                                                        datetime.now(),
                                                        vuid1,
                                                        vn1, vn2)))
        self.assertIsInstance(vn3, uuid.UUID)


if __name__ == '__main__':
    unittest.main()
