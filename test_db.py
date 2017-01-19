import unittest
from pim import *
from db import *


class TestPIM(unittest.TestCase):
    # def setUp(self):
    #     pass

    @staticmethod
    def _get_test_password():
        return 'kLF9AW8IA0H5WiLcoByZF9H3Yl7FXtBU'

    def test_db(self):
        db = DataBase('test_db.data', self._get_test_password)

        n1 = db.append(PermanentRecord(Note("Note title 1", "Note text 1\nNote text 1")))
        self.assertIsInstance(n1, uuid.UUID)
        print(db[n1])

    def disabled_test_db(self):
        db = DataBase('test_db.data', self._get_test_password)

        n1 = db.append(PermanentRecord(Note("Note title 1", "Note text 1\nNote text 1")))
        n2 = db.append(PermanentRecord(Note("Note title 2", "Note text 2\nNote text 2")))
        n3 = db.append(PermanentRecord(Note("Note title 3", "Note text 3\nNote text 3")))

        t1 = db.append(PermanentRecord(Task("Task 1")))
        t2 = db.append(PermanentRecord(Task("Task 2")))
        t3 = db.append(PermanentRecord(Task("Task 3")))
        t4 = db.append(PermanentRecord(Task("Task 4")))

        print(n1, n2, n3)
        print(t1, t2, t3, t4)

        self.assertIsInstance(n1, uuid.UUID)
        self.assertIsInstance(n2, uuid.UUID)
        self.assertIsInstance(n3, uuid.UUID)
        self.assertIsInstance(t1, uuid.UUID)
        self.assertIsInstance(t2, uuid.UUID)
        self.assertIsInstance(t3, uuid.UUID)
        self.assertIsInstance(t4, uuid.UUID)
        self.assertEqual(db[t1], Task("Task 1"))

        n1 = db.append(EncryptedRecord(Note("E Note title 1", "Note text 1\nNote text 1"), self._get_test_password))
        n2 = db.append(EncryptedRecord(Note("E Note title 2", "Note text 2\nNote text 2"), self._get_test_password))
        n3 = db.append(EncryptedRecord(Note("E Note title 3", "Note text 3\nNote text 3"), self._get_test_password))

        t1 = db.append(EncryptedRecord(Task("E Task 1"), self._get_test_password))
        t2 = db.append(EncryptedRecord(Task("E Task 2"), self._get_test_password))
        t3 = db.append(EncryptedRecord(Task("E Task 3"), self._get_test_password))
        t4 = db.append(EncryptedRecord(Task("E Task 4"), self._get_test_password))

        print(n1, n2, n3)
        print(t1, t2, t3, t4)

        self.assertIsInstance(n1, uuid.UUID)
        self.assertIsInstance(n2, uuid.UUID)
        self.assertIsInstance(n3, uuid.UUID)
        self.assertIsInstance(t1, uuid.UUID)
        self.assertIsInstance(t2, uuid.UUID)
        self.assertIsInstance(t3, uuid.UUID)
        self.assertIsInstance(t4, uuid.UUID)


if __name__ == '__main__':
    unittest.main()
