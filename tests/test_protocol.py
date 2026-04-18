"""
Unit tests for the Protocol class
"""
import unittest
import time
from queue import PriorityQueue, Empty
from protocol import Protocol, ProtocolError
from message import Message


class TestProtocol(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = Protocol()

    def tearDown(self):
        """Clean up test fixtures"""
        del self.protocol

    def test_init_default(self):
        """Test Protocol initialization with default values"""
        protocol = Protocol()
        self.assertEqual(protocol.registered_modules, {})
        self.assertIsNone(protocol.main_address)

    def test_init_with_main_address(self):
        """Test Protocol initialization with main address"""
        protocol = Protocol("main")
        self.assertEqual(protocol.main_address, "main")
        self.assertIn("main", protocol.registered_modules)
        self.assertIsInstance(protocol.registered_modules["main"], PriorityQueue)

    def test_str(self):
        """Test string representation"""
        protocol = Protocol("main")
        str_repr = str(protocol)
        self.assertIn("main_address=main", str_repr)
        self.assertIn("registered_modules", str_repr)

    def test_repr(self):
        """Test repr representation"""
        protocol = Protocol("main")
        repr_str = repr(protocol)
        self.assertIn("main_address=main", repr_str)
        self.assertIn("registered_modules", repr_str)

    def test_eq_equal(self):
        """Test equality when protocols are equal"""
        p1 = Protocol("main")
        p2 = Protocol("main")
        self.assertEqual(p1, p2)

    def test_eq_not_equal(self):
        """Test equality when protocols differ"""
        p1 = Protocol("main")
        p2 = Protocol("other")
        self.assertNotEqual(p1, p2)

    def test_eq_not_protocol(self):
        """Test equality with non-Protocol object"""
        protocol = Protocol()
        self.assertNotEqual(protocol, "not a protocol")

    def test_hash(self):
        """Test hash function"""
        p1 = Protocol("main")
        p2 = Protocol("main")
        self.assertEqual(hash(p1), hash(p2))

    def test_get_module_names_empty(self):
        """Test get_module_names with no modules"""
        self.assertEqual(self.protocol.get_module_names(), [])

    def test_get_module_names_with_modules(self):
        """Test get_module_names with registered modules"""
        self.protocol.register_module("module1")
        self.protocol.register_module("module2")
        names = self.protocol.get_module_names()
        self.assertIn("module1", names)
        self.assertIn("module2", names)

    def test_register_module_success(self):
        """Test successful module registration"""
        self.protocol.register_module("test_module")
        self.assertIn("test_module", self.protocol.registered_modules)
        self.assertIsInstance(self.protocol.registered_modules["test_module"], PriorityQueue)

    def test_register_module_duplicate(self):
        """Test registering a module that already exists"""
        self.protocol.register_module("test_module")
        with self.assertRaises(ProtocolError) as cm:
            self.protocol.register_module("test_module")
        self.assertIn("already registered", str(cm.exception))

    def test_unregister_module_success(self):
        """Test successful module unregistration"""
        self.protocol.register_module("test_module")
        self.protocol.unregister_module("test_module")
        self.assertNotIn("test_module", self.protocol.registered_modules)

    def test_unregister_module_not_found(self):
        """Test unregistering a non-existent module"""
        with self.assertRaises(ProtocolError) as cm:
            self.protocol.unregister_module("nonexistent")
        self.assertIn("No module registered", str(cm.exception))

    def test_send_action_success(self):
        """Test successful send_action"""
        self.protocol.register_module("target")
        self.protocol.send_action("target", "test_command", b"payload")
        # Check that message was queued
        message = self.protocol.receive_message("target")
        self.assertEqual(message.address, "target")
        self.assertEqual(message.command, "test_command")
        self.assertEqual(message.payload, b"payload")

    def test_send_action_no_module(self):
        """Test send_action to non-existent module"""
        with self.assertRaises(ProtocolError) as cm:
            self.protocol.send_action("nonexistent", "command")
        self.assertIn("No module registered", str(cm.exception))

    def test_send_request_success(self):
        """Test successful send_request"""
        self.protocol.register_module("target")
        # Start a thread to handle the request
        import threading
        def handler():
            try:
                msg = self.protocol.receive_message("target", timeout=1.0)
                if msg.command == "test_request":
                    self.protocol.send_response(msg, "response_data")
            except:
                pass

        thread = threading.Thread(target=handler)
        thread.start()

        response = self.protocol.send_request("target", "test_request", timeout=2.0)
        thread.join()
        self.assertEqual(response, "response_data")

    def test_send_request_timeout(self):
        """Test send_request timeout"""
        self.protocol.register_module("target")
        with self.assertRaises(TimeoutError):
            self.protocol.send_request("target", "command", timeout=0.1)

    def test_send_request_no_module(self):
        """Test send_request to non-existent module"""
        with self.assertRaises(ProtocolError) as cm:
            self.protocol.send_request("nonexistent", "command")
        self.assertIn("No module registered", str(cm.exception))

    def test_send_response_success(self):
        """Test successful send_response"""
        response_queue = PriorityQueue()
        source_msg = Message("addr", "cmd", source=response_queue)
        self.protocol.send_response(source_msg, "response")
        priority, response = response_queue.get()
        self.assertEqual(response, "response")

    def test_send_response_no_source(self):
        """Test send_response with no source queue"""
        source_msg = Message("addr", "cmd")
        with self.assertRaises(ProtocolError) as cm:
            self.protocol.send_response(source_msg, "response")
        self.assertIn("does not have a return address", str(cm.exception))

    def test_receive_message_success(self):
        """Test successful receive_message"""
        self.protocol.register_module("test_module")
        test_msg = Message("test_module", "command", "payload")
        self.protocol.registered_modules["test_module"].put((99, test_msg))

        received = self.protocol.receive_message("test_module")
        self.assertEqual(received, test_msg)

    def test_receive_message_no_module(self):
        """Test receive_message from non-existent module"""
        with self.assertRaises(ProtocolError) as cm:
            self.protocol.receive_message("nonexistent")
        self.assertIn("No module registered", str(cm.exception))

    def test_receive_message_timeout(self):
        """Test receive_message timeout"""
        self.protocol.register_module("test_module")
        with self.assertRaises(TimeoutError):
            self.protocol.receive_message("test_module", timeout=0.1)

    def test_broadcast_message(self):
        """Test broadcast_message"""
        self.protocol.register_module("module1")
        self.protocol.register_module("module2")
        self.protocol.register_module("module3")

        self.protocol.broadcast_message("broadcast_cmd", b"data")

        # Check that all modules received the message
        for module in ["module1", "module2", "module3"]:
            msg = self.protocol.receive_message(module)
            self.assertEqual(msg.command, "broadcast_cmd")
            self.assertEqual(msg.payload, b"data")
            self.assertEqual(msg.address, module)

    def test_get_registered_modules(self):
        """Test get_registered_modules"""
        self.protocol.register_module("mod1")
        self.protocol.register_module("mod2")
        modules = self.protocol.get_registered_modules()
        self.assertIn("mod1", modules)
        self.assertIn("mod2", modules)


if __name__ == '__main__':
    unittest.main()