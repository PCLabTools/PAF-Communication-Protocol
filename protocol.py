"""
file: protocol.py
description: Defines the Protocol class for managing communication between modules in the Python Actor Framework, along with a custom exception class for protocol-related errors.
author: PCLabTools (https://github.com/PCLabTools)
"""

from .message import Message
from typing import Any, Optional
from queue import Empty, PriorityQueue

class Protocol:
    
    def __init__(self, main_address: Optional[str] = None):
        """Initialises the protocol with an empty registry of modules

        Args:
            main_address (str, optional): The address to use for the main module. Defaults to "main".
        """
        self.registered_modules: dict[str, PriorityQueue] = {}
        self.main_address = main_address
        if self.main_address is not None:
            self.register_module(self.main_address)

    def __del__(self):
        """Cleans up the protocol by clearing the registry of modules
        """
        self.main_address = None
        self.registered_modules.clear()

    def __str__(self) -> str:
        """Returns a string representation of the protocol for debugging purposes

        Returns:
            str: A string representation of the protocol
        """
        return f"Protocol(main_address={self.main_address}, registered_modules={self.registered_modules.keys()})"
    
    def __repr__(self) -> str:
        """Returns a detailed string representation of the protocol for debugging purposes

        Returns:
            str: A detailed string representation of the protocol
        """
        return f"Protocol(main_address={self.main_address}, registered_modules={self.registered_modules})"
    
    def __eq__(self, other) -> bool:
        """Checks if this protocol is equal to another protocol based on their main addresses and registered modules

        Args:
            other (Protocol): The other protocol to compare against

        Returns:
            bool: True if the protocols are equal, False otherwise
        """
        if not isinstance(other, Protocol):
            return False
        return (self.main_address == other.main_address and
                set(self.registered_modules.keys()) == set(other.registered_modules.keys()))
    
    def __hash__(self) -> int:
        """Returns a hash value for the protocol based on its main address and registered modules

        Returns:
            int: A hash value for the protocol
        """
        return hash((self.main_address, frozenset(self.registered_modules.keys())))
    
    def get_module_names(self) -> list:
        """Returns a list of the names of all registered modules

        Returns:
            list: A list of registered module names
        """
        return list(self.registered_modules.keys())

    def register_module(self, module_name: str):
        """Registers a module with the protocol by associating its name with a message queue

        Args:
            module_name (str): The name of the module to register

        Raises:
            ProtocolError: If a module with the same name is already registered
        """
        if module_name not in self.registered_modules:
            self.registered_modules[module_name] = PriorityQueue()
        else:
            raise ProtocolError(f"Module with name {module_name} is already registered")
        

    def unregister_module(self, module_name: str):
        """Unregisters a module from the protocol

        Args:
            module_name (str): The name of the module to unregister

        Raises:
            ProtocolError: If no module with the specified name is registered
        """
        if module_name in self.registered_modules:
            del self.registered_modules[module_name]
        else:
            raise ProtocolError(f"No module registered with name {module_name}")

    def _send_message(self, message: Message, priority: Optional[int] = 99):
        """Internal method to send a message to the appropriate module's queue

        Args:
            message (Message): The message to send
            priority (int, optional): The priority of the message. Defaults to 99.

        Raises:
            ProtocolError: If no module with the specified address is registered
        """
        if message.address in self.registered_modules:
            self.registered_modules[message.address].put((priority, message))
        else:
            raise ProtocolError(f"No module registered with address {message.address}")
        
    def receive_message(self, module_name: str, timeout: Optional[float] = None) -> Message:
        """Receives a message from the specified module's queue

        Args:
            module_name (str): The name of the module to receive a message from
            timeout (float, optional): The maximum time to wait for a message before raising an error. Defaults to None.

        Raises:
            ProtocolError: If no module with the specified name is registered
            TimeoutError: If no message is received within the specified timeout

        Returns:
            Message: The message received from the module's queue
        """
        if module_name not in self.registered_modules:
            raise ProtocolError(f"No module registered with name {module_name}")
        try:
            qpriority, message = self.registered_modules[module_name].get(timeout=timeout)
        except Empty:
            raise TimeoutError(f"No message received from module {module_name} within timeout of {timeout} seconds")
        return message
        
    def send_action(self, address: str, command: str, payload: Optional[bytes] = None, priority: Optional[int] = 99):
        """Sends an action message to the specified address with the given command and optional payload

        Args:
            address (str): The target address for the message
            command (str): The command or action to be performed by the target module
            payload (bytes, optional): Optional data to be included with the message. Defaults to None.
            priority (int, optional): The priority of the message. Defaults to 99.

        Raises:
            ProtocolError: If no module with the specified address is registered
        """
        message = Message(address=address, command=command, payload=payload, source=None)
        self._send_message(message, priority=priority)

    def send_request(self, address: str, command: str, payload: Optional[bytes] = None, priority: Optional[int] = 99, timeout: Optional[float] = None) -> Any:
        """Sends a request message to the specified address with the given command, optional payload, and optional return address for responses

        Args:
            address (str): The target address for the message
            command (str): The command or action to be performed by the target module
            payload (bytes, optional): Optional data to be included with the message. Defaults to None.
            priority (int, optional): The priority of the message. Defaults to 99.
            timeout (float, optional): The maximum time to wait for a response before raising an error. Defaults to None.

        Raises:
            TimeoutError: If no response is received within the specified timeout
            ProtocolError: If no module with the specified address is registered

        Returns:
            Message: The response message received from the target module
        """
        response_queue = PriorityQueue()
        message = Message(address=address, command=command, payload=payload, source=response_queue)
        self._send_message(message, priority=priority)
        try:
            qpriority, response = response_queue.get(timeout=timeout)
        except Empty:
            raise TimeoutError(f"No response received from address {address} within timeout of {timeout} seconds")
        finally:
            del response_queue  # Clean up the response queue after use
        return response

    def send_response(self, source_message: Message, response: Any):
        """Sends a response message to the specified address with the given command and optional payload

        Args:
            source_message (Message): The original message that the response is replying to, which should contain a return address in its source field
            response (Any): The response data to be included with the response message.

        Raises:
            ProtocolError: If the source message does not have a return address
        """
        if source_message.source is None:
            raise ProtocolError("Source message does not have a return address")
        source_message.source.put((0, response))
        
    def broadcast_message(self, command: str, payload: Optional[bytes] = None, priority: Optional[int] = 99):
        """Sends a message with the specified command and optional payload to all registered modules

        Args:
            command (str): The command or action to be performed by the target modules
            payload (bytes, optional): Optional data to be included with the message. Defaults to None.
        """
        for module_name in self.registered_modules.keys():
            message = Message(address=module_name, command=command, payload=payload)
            self._send_message(message, priority)

    def get_registered_modules(self) -> list:
        """Returns a list of the names of all registered modules
        
        Returns:
            list: A list of registered module names
        """
        return list(self.registered_modules.keys())


class ProtocolError(Exception):
    """Custom exception class for protocol-related errors
    """
    pass
