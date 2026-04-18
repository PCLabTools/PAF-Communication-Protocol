"""
file: module.py
description: Defines the Module class for representing individual modules in the Python Actor Framework, including methods for handling messages and performing background tasks.
author: PCLabTools (https://github.com/PCLabTools)
"""

from .protocol import Protocol
from .message import Message
from threading import Thread

class Module:
    
    def __init__(self, address: str, protocol: Protocol):
        """Initializes a module with the specified address and protocol, registers itself with the protocol, and starts its message handling thread
        
        Args:
            address (str): The unique address for the module to register with the protocol
            protocol (Protocol): The protocol instance to register with and use for communication
        """
        self.address = address
        self.protocol = protocol
        self.protocol.register_module(self.address)
        self.thread = Thread(target=self.run)
        try:
            if self.debug >= 99: print(f"{self.__class__.__name__} ({self.address}): Module initialized and registered with protocol.")
        except:
            pass
        self.thread.start()
        self.background_task_thread = Thread(target=self.background_task)
        self.background_task_running = False

    def __del__(self):
        """Unregisters the module from the protocol when it is destroyed
        """
        try:
            if self.debug >= 99: print(f"{self.__class__.__name__} ({self.address}): Unregistering module from protocol.")
        except:
            pass
        try:
            self.protocol.unregister_module(self.address)
        except:
            pass

    def run(self):
        """Main loop for the module to continuously process incoming messages
        """
        try:
            if self.debug >= 99: print(f"{self.__class__.__name__} ({self.address}): Starting main loop.")
        except:
            pass
        while True:
            message = self.protocol.receive_message(self.address)
            if self.handle_message(message):
                break

    def handle_message(self, message: Message) -> bool:
        """Handles an incoming message and returns True if the module should stop running, otherwise False

        Args:
            message (Message): The incoming message to handle

        Returns:
            bool: True if the module should stop running, False otherwise
        """
        if message.command == "shutdown":
            try:
                if self.debug >= 99: print(f"{self.__class__.__name__} ({self.address}): Received shutdown command. Shutting down.")
            except:
                pass
            return True
        if message.command == "start":
            try:
                if self.debug >= 99: print(f"{self.__class__.__name__} ({self.address}): Received start command. Starting background task.")
            except:
                pass
            if not self.background_task_running:
                self.background_task_thread.start()
                self.background_task_running = True
            return False
        if message.command == "stop":
            try:
                if self.debug >= 99: print(f"{self.__class__.__name__} ({self.address}): Received stop command. Stopping background task.")
            except:
                pass
            if self.background_task_running:
                self.background_task_running = False
                self.background_task_thread.join()
            return False
        if message.command == "status":
            try:
                if self.debug >= 99: print(f"{self.__class__.__name__} ({self.address}): Received status command. Sending status response.")
            except:
                pass
            self.protocol.send_response(message, f"Module {self.address} is {('running' if self.background_task_running else 'not running')}")
            return False
        raise NotImplementedError("Subclasses must implement handle_message method for {message.command} command")

    def background_task(self):
        """Background task that the module can perform while running (optional)
        """
        raise NotImplementedError("Subclasses can implement background_task method if needed for {self.address} module")