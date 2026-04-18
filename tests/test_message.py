"""
Unit tests for the Message class
"""
import unittest
from queue import PriorityQueue
from message import Message


class TestMessage(unittest.TestCase):

    def test_init(self):
        """Test Message initialization"""
        msg = Message("test_address", "test_command", {"key": "value"})
        self.assertEqual(msg.address, "test_address")
        self.assertEqual(msg.command, "test_command")
        self.assertEqual(msg.payload, {"key": "value"})
        self.assertIsNone(msg.source)

    def test_init_with_source(self):
        """Test Message initialization with source"""
        source_queue = PriorityQueue()
        msg = Message("test_address", "test_command", None, source_queue)
        self.assertEqual(msg.source, source_queue)

    def test_str(self):
        """Test string representation"""
        msg = Message("addr", "cmd", {"data": 123})
        expected = "Message(address=addr, command=cmd, payload={'data': 123}, source=None)"
        self.assertEqual(str(msg), expected)

    def test_repr(self):
        """Test repr representation"""
        msg = Message("addr", "cmd")
        self.assertEqual(repr(msg), str(msg))

    def test_eq_equal(self):
        """Test equality when messages are equal"""
        msg1 = Message("addr", "cmd", {"key": "val"})
        msg2 = Message("addr", "cmd", {"key": "val"})
        self.assertEqual(msg1, msg2)

    def test_eq_not_equal_address(self):
        """Test equality when addresses differ"""
        msg1 = Message("addr1", "cmd", {"key": "val"})
        msg2 = Message("addr2", "cmd", {"key": "val"})
        self.assertNotEqual(msg1, msg2)

    def test_eq_not_equal_command(self):
        """Test equality when commands differ"""
        msg1 = Message("addr", "cmd1", {"key": "val"})
        msg2 = Message("addr", "cmd2", {"key": "val"})
        self.assertNotEqual(msg1, msg2)

    def test_eq_not_equal_payload(self):
        """Test equality when payloads differ"""
        msg1 = Message("addr", "cmd", {"key": "val1"})
        msg2 = Message("addr", "cmd", {"key": "val2"})
        self.assertNotEqual(msg1, msg2)

    def test_eq_not_equal_source(self):
        """Test equality when sources differ"""
        source1 = PriorityQueue()
        source2 = PriorityQueue()
        msg1 = Message("addr", "cmd", None, source1)
        msg2 = Message("addr", "cmd", None, source2)
        self.assertNotEqual(msg1, msg2)

    def test_eq_not_message(self):
        """Test equality with non-Message object"""
        msg = Message("addr", "cmd")
        self.assertNotEqual(msg, "not a message")

    def test_lt(self):
        """Test less-than comparison (always False)"""
        msg1 = Message("addr1", "cmd")
        msg2 = Message("addr2", "cmd")
        self.assertFalse(msg1 < msg2)
        self.assertFalse(msg2 < msg1)

    def test_lt_not_message(self):
        """Test less-than with non-Message object"""
        msg = Message("addr", "cmd")
        with self.assertRaises(TypeError):
            msg < "not a message"

    def test_hash(self):
        """Test hash function"""
        msg1 = Message("addr", "cmd", {"key": "val"})
        msg2 = Message("addr", "cmd", {"key": "val"})
        self.assertEqual(hash(msg1), hash(msg2))

    def test_hash_different(self):
        """Test hash function with different messages"""
        msg1 = Message("addr1", "cmd", {"key": "val"})
        msg2 = Message("addr2", "cmd", {"key": "val"})
        self.assertNotEqual(hash(msg1), hash(msg2))


if __name__ == '__main__':
    unittest.main()