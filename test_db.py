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

        self.assertEqual(note.title, "title")
        self.assertEqual(task.title, "title")
        self.assertEqual(category.title, "title")
        self.assertEqual(url.title, "title")
        self.assertEqual(project.title, "title")
        self.assertEqual(target.title, "title")
        self.assertEqual(password.service, "title")

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

        en1 = db.append(EncryptedRecord(Note("E Note title 1", "Note text 1\nNote text 1"), self._get_test_password))
        en2 = db.append(EncryptedRecord(Note("E Note title 2", "Note text 2\nNote text 2"), self._get_test_password))
        en3 = db.append(EncryptedRecord(Note("E Note title 3", "Note text 3\nNote text 3"), self._get_test_password))

        et1 = db.append(EncryptedRecord(Task("E Task 1"), self._get_test_password))
        et2 = db.append(EncryptedRecord(Task("E Task 2"), self._get_test_password))
        et3 = db.append(EncryptedRecord(Task("E Task 3"), self._get_test_password))
        et4 = db.append(EncryptedRecord(Task("E Task 4"), self._get_test_password))

        self.assertIsInstance(en1, uuid.UUID)
        self.assertIsInstance(en2, uuid.UUID)
        self.assertIsInstance(en3, uuid.UUID)

        self.assertIsInstance(et1, uuid.UUID)
        self.assertIsInstance(et2, uuid.UUID)
        self.assertIsInstance(et3, uuid.UUID)
        self.assertIsInstance(et4, uuid.UUID)

        self.assertIsInstance(db[en1], Note)
        self.assertIsInstance(db[en2], Note)
        self.assertIsInstance(db[en3], Note)

        self.assertIsInstance(db[et1], Task)
        self.assertIsInstance(db[et2], Task)
        self.assertIsInstance(db[et3], Task)
        self.assertIsInstance(db[et4], Task)

        assert_note_title(db[en1], "E Note title 1")
        assert_note_title(db[en2], "E Note title 2")
        assert_note_title(db[en3], "E Note title 3")

        assert_task_title(db[et1], Task("E Task 1").title)
        assert_task_title(db[et2], Task("E Task 2").title)
        assert_task_title(db[et3], Task("E Task 3").title)
        assert_task_title(db[et4], Task("E Task 4").title)

        # Test delete marks

        d2 = db.append(PermanentRecord(DeleteMark(n2)))
        d3 = db.append(PermanentRecord(DeleteMark(n3)))
        r3 = db.append(PermanentRecord(RevertMark(d3)))

        self.assertIsInstance(d2, uuid.UUID)
        self.assertIsInstance(d3, uuid.UUID)
        self.assertIsInstance(r3, uuid.UUID)

        # self.assertTrue(db.actual[n1])
        # self.assertFalse(db.actual[n2])
        # self.assertTrue(db.actual[n3])

        # Reopen database

        db2 = DataBase('test_db.data', self._get_test_password)

        for k in [n1, n2, n3, t1, t2, t3, t4, en1, en2, en3, et1, et2, et3, et4]:
            try:
                self.assertIsInstance(db2[k], Record)
            except KeyError:
                self.fail('previously added key not in db')

        self.assertTrue(db2.actual[n1])
        self.assertFalse(db2.actual[n2])
        self.assertTrue(db2.actual[n3])

        # Now test temporary records

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

        self.assertIsInstance(db2[n1], Note)
        self.assertIsInstance(db2[n2], Note)
        self.assertIsInstance(db2[n3], Note)

        self.assertIsInstance(db2[t1], Task)
        self.assertIsInstance(db2[t2], Task)
        self.assertIsInstance(db2[t3], Task)
        self.assertIsInstance(db2[t4], Task)

        assert_note_title(db2[n1], "Note title 1")
        assert_note_title(db2[n2], "Note title 2")
        assert_note_title(db2[n3], "Note title 3")

        assert_task_title(db2[t1], Task("Task 1").title)
        assert_task_title(db2[t2], Task("Task 2").title)
        assert_task_title(db2[t3], Task("Task 3").title)
        assert_task_title(db2[t4], Task("Task 4").title)

    def test_db_versioned(self):
        os.unlink('test_db.data')
        db = DataBase('test_db.data', self._get_test_password)

        _ = db.append(PermanentRecord(Note("Note title 1", "Note text 1\nNote text 1")))
        _ = db.append(PermanentRecord(Note("Note title 2", "Note text 2\nNote text 2")))
        _ = db.append(PermanentRecord(Note("Note title 3", "Note text 3\nNote text 3")))

        _ = db.append(PermanentRecord(Task("Task 1")))
        _ = db.append(PermanentRecord(Task("Task 2")))
        _ = db.append(PermanentRecord(Task("Task 3")))
        _ = db.append(PermanentRecord(Task("Task 4")))

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

        db2 = DataBase('test_db.data', self._get_test_password)

        self.assertIsInstance(db2[vn1], VersionedRecord)
        self.assertIsInstance(db2[vn2], VersionedRecord)
        self.assertIsInstance(db2[vn3], VersionedRecord)

        self.assertIsInstance(db2[vn1].record, Note)
        self.assertIsInstance(db2[vn2].record, Note)
        self.assertIsInstance(db2[vn3].record, Note)

        self.assertIsInstance(db2.get_versions(vuid1), dict)


if __name__ == '__main__':
    unittest.main()
