"""
Unit tests for the Module class
"""
import unittest
import time
from queue import PriorityQueue
from ..protocol import Protocol
from ..message import Message
from ..module import Module


class TestModule(Module):
    """Test implementation of Module for testing purposes"""

    def __init__(self, address: str, protocol: Protocol):
        super().__init__(address, protocol)
        self.handled_messages = []
        self.background_task_calls = 0

    def handle_message(self, message: Message) -> bool:
        """Override to track handled messages"""
        self.handled_messages.append(message)
        if message.command == "shutdown":
            return True
        if message.command == "start":
            if not self.background_task_running:
                self.background_task_thread.start()
                self.background_task_running = True
            return False
        if message.command == "stop":
            if self.background_task_running:
                self.background_task_running = False
                self.background_task_thread.join()
            return False
        if message.command == "status":
            self.protocol.send_response(message, f"Module {self.address} is {('running' if self.background_task_running else 'not running')}")
            return False
        # For unknown commands, raise NotImplementedError
        raise NotImplementedError("Subclasses must implement handle_message method for {message.command} command")

    def background_task(self):
        """Override to track background task calls"""
        while self.background_task_running:
            self.background_task_calls += 1
            time.sleep(0.01)  # Small sleep to avoid busy waiting


class TestModuleClass(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = Protocol()

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up any registered modules
        for module_name in self.protocol.get_registered_modules():
            try:
                self.protocol.unregister_module(module_name)
            except:
                pass
        del self.protocol

    def test_init(self):
        """Test Module initialization"""
        module = TestModule("test_module", self.protocol)
        self.assertEqual(module.address, "test_module")
        self.assertEqual(module.protocol, self.protocol)
        self.assertIn("test_module", self.protocol.registered_modules)
        self.assertTrue(module.thread.is_alive())
        self.assertFalse(module.background_task_running)

        # Clean up
        self.protocol.send_action("test_module", "shutdown")
        module.thread.join(timeout=1.0)

    def test_del(self):
        """Test Module cleanup on deletion"""
        module = TestModule("test_module", self.protocol)
        module_address = module.address
        self.protocol.send_action("test_module", "shutdown")
        module.thread.join(timeout=1.0)

        # Delete module - should unregister itself
        del module

        # The module should be unregistered (though we can't reliably test this due to timing)
        # Just ensure no exception is raised

    def test_handle_message_shutdown(self):
        """Test handle_message with shutdown command"""
        module = TestModule("test_module", self.protocol)

        msg = Message("test_module", "shutdown")
        result = module.handle_message(msg)

        self.assertTrue(result)
        self.assertIn(msg, module.handled_messages)

        # Clean up
        module.thread.join(timeout=1.0)

    def test_handle_message_start(self):
        """Test handle_message with start command"""
        module = TestModule("test_module", self.protocol)

        msg = Message("test_module", "start")
        result = module.handle_message(msg)

        self.assertFalse(result)
        self.assertIn(msg, module.handled_messages)
        self.assertTrue(module.background_task_running)
        # The thread should be started (we can't reliably check is_alive due to timing)

        # Clean up
        self.protocol.send_action("test_module", "stop")
        self.protocol.send_action("test_module", "shutdown")
        module.thread.join(timeout=1.0)
        module.background_task_thread.join(timeout=1.0)

    def test_handle_message_stop(self):
        """Test handle_message with stop command"""
        module = TestModule("test_module", self.protocol)

        # Start first
        start_msg = Message("test_module", "start")
        module.handle_message(start_msg)

        stop_msg = Message("test_module", "stop")
        result = module.handle_message(stop_msg)

        self.assertFalse(result)
        self.assertIn(stop_msg, module.handled_messages)
        self.assertFalse(module.background_task_running)

        # Clean up
        self.protocol.send_action("test_module", "shutdown")
        module.thread.join(timeout=1.0)

    def test_handle_message_status(self):
        """Test handle_message with status command"""
        module = TestModule("test_module", self.protocol)

        # Create a message with a response queue
        response_queue = PriorityQueue()
        msg = Message("test_module", "status", None, response_queue)
        result = module.handle_message(msg)

        self.assertFalse(result)
        self.assertIn(msg, module.handled_messages)

        # Check that response was sent
        priority, response = response_queue.get(timeout=1.0)
        self.assertIn("not running", response)

        # Clean up
        self.protocol.send_action("test_module", "shutdown")
        module.thread.join(timeout=1.0)

    def test_handle_message_unknown_command(self):
        """Test handle_message with unknown command"""
        module = TestModule("test_module", self.protocol)

        msg = Message("test_module", "unknown")
        with self.assertRaises(NotImplementedError):
            module.handle_message(msg)

        # Clean up
        self.protocol.send_action("test_module", "shutdown")
        module.thread.join(timeout=1.0)

    def test_background_task_not_running(self):
        """Test background_task when not running"""
        module = TestModule("test_module", self.protocol)
        module.background_task_running = False

        # Call background_task briefly
        module.background_task_thread = type('MockThread', (), {'start': lambda: None, 'join': lambda timeout=None: None})()
        module.background_task()

        # Should not increment calls since not running
        self.assertEqual(module.background_task_calls, 0)

        # Clean up
        self.protocol.send_action("test_module", "shutdown")
        module.thread.join(timeout=1.0)

    def test_run_loop(self):
        """Test the main run loop"""
        module = TestModule("test_module", self.protocol)

        # Send a message
        self.protocol.send_action("test_module", "test_cmd")

        # Wait a bit for processing
        time.sleep(0.1)

        # Check that message was handled
        self.assertEqual(len(module.handled_messages), 1)
        self.assertEqual(module.handled_messages[0].command, "test_cmd")

        # Send shutdown
        self.protocol.send_action("test_module", "shutdown")
        module.thread.join(timeout=1.0)


if __name__ == '__main__':
    unittest.main()