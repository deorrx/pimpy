import unittest
from pim import *
from db import import *


class TestPIM(unittest.TestCase):
    def setUp(self):
        pass


    def test_pim(self):
        db = DataBase('test_pim.data', get_test_password)

        if len(sys.argv) == 2 and sys.argv[1] == '-s':
            n1 = db.append(PermanentRecord(Note("Note title 1", "Note text 1\nNote text 1")))
            n2 = db.append(PermanentRecord(Note("Note title 2", "Note text 2\nNote text 2")))
            n3 = db.append(PermanentRecord(Note("Note title 3", "Note text 3\nNote text 3")))

            t1 = db.append(PermanentRecord(Task("Task 1")))
            t2 = db.append(PermanentRecord(Task("Task 2")))
            t3 = db.append(PermanentRecord(Task("Task 3")))
            t4 = db.append(PermanentRecord(Task("Task 4")))

            print(n1, n2, n3)
            print(t1, t2, t3, t4)

            n1 = db.append(EncryptedRecord(Note("E Note title 1", "Note text 1\nNote text 1"), get_test_password))
            n2 = db.append(EncryptedRecord(Note("E Note title 2", "Note text 2\nNote text 2"), get_test_password))
            n3 = db.append(EncryptedRecord(Note("E Note title 3", "Note text 3\nNote text 3"), get_test_password))

            t1 = db.append(EncryptedRecord(Task("E Task 1"), get_test_password))
            t2 = db.append(EncryptedRecord(Task("E Task 2"), get_test_password))
            t3 = db.append(EncryptedRecord(Task("E Task 3"), get_test_password))
            t4 = db.append(EncryptedRecord(Task("E Task 4"), get_test_password))

            print(n1, n2, n3)
            print(t1, t2, t3, t4)

        if len(sys.argv) == 2 and sys.argv[1] == '-l':
            print(db.keys())

        if len(sys.argv) == 3 and sys.argv[1] == '-d':
            print(db[uuid.UUID(sys.argv[2])])



if __name__ == '__main__':
    unittest.main()
