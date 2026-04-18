"""
file: message.py
description: Defines the Message class for representing messages sent between modules in the Python Actor Framework, including attributes for address, command, payload, and source.
author: PCLabTools (https://github.com/PCLabTools)
"""

from typing import Any, Optional
from queue import PriorityQueue

class Message:
    
    def __init__(self, address: str, command: str, payload: Optional[dict[str, Any]] = None, source: Optional[PriorityQueue] = None):
        """Initializes a message with the specified address, command, optional payload, and optional return address
        
        Args:
            address (str): The target address for the message
            command (str): The command or action to be performed by the target module
            payload (dict[str, Any], optional): Optional data to be included with the message. Defaults to None.
            source (PriorityQueue, optional): Optional return address for responses. Defaults to None.
        """
        self.address = address
        self.command = command
        self.payload = payload
        self.source = source

    def __str__(self) -> str:
        """Returns a string representation of the message for debugging purposes

        Returns:
            str: A string representation of the message
        """
        return f"Message(address={self.address}, command={self.command}, payload={self.payload}, source={self.source})"
    
    def __repr__(self) -> str:
        """Returns a string representation of the message for debugging purposes

        Returns:
            str: A string representation of the message
        """
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """Checks if this message is equal to another message based on address, command, payload, and source

        Args:
            other (Message): The other message to compare against

        Returns:
            bool: True if the messages are equal, False otherwise
        """
        if not isinstance(other, Message):
            return NotImplemented
        return self.address == other.address and self.command == other.command and self.payload == other.payload and self.source == other.source
    
    def __lt__(self, other) -> bool:
        """Defines a less-than comparison for messages based on their address, command, payload, and source

        Args:
            other (Message): The other message to compare against

        Returns:
            bool: True if this message is less than the other, False otherwise
        """
        if not isinstance(other, Message):
            return NotImplemented
        return False

    def __hash__(self) -> int:
        """Returns a hash value for the message based on its address, command, payload, and source

        Returns:
            int: A hash value for the message
        """
        # Convert payload to hashable form
        payload_hash = None
        if self.payload is not None:
            if isinstance(self.payload, dict):
                payload_hash = frozenset(self.payload.items())
            else:
                payload_hash = self.payload
        
        return hash((self.address, self.command, payload_hash, self.source))