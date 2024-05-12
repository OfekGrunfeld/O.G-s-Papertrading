from enum import Enum
from uuid import uuid4
from typing import Literal, Optional, Tuple
from dataclasses import dataclass, field, fields
from datetime import datetime

import numpy as np

from records.helper import BetterDataclass

# has to be here otherwise a circual import error will occur
def generate_uuid() -> str:
    """
    Returns:
        str: A uuid4 formatted as a string.
    """
    return str(uuid4())

# Stock Records
class Statuses(Enum):
    """
    Enumeration representing the status of a stock record within a trading system.

    Attributes:
        pending (str): Status indicating a stock record is waiting for action.
        tracked (str): Status indicating a stock record is currently being tracked, 
                        meaning it is part of the active portfolio.
        archived (str): Status indicating a stock record is archived and not active, 
                        meaning it is not a part of the active portfolio.
    """
    pending = "pending"  
    tracked = "tracked"  
    archived = "archived" 

@dataclass
class StockRecord(BetterDataclass):
    """
    Data class representing a stock transaction record.

    Attributes:
        uid (str): Unique identifier for the stock record, generated upon initialization.
        timestamp (datetime): Timestamp when the stock record was created, defaults to the current datetime.
        symbol (str): Stock symbol.
        side (Literal["buy", "sell"]): Side of the trade, either 'buy' or 'sell'.
        order_type (Literal["market", "limit", "stop", "stop_limit"]): Type of stock order.
        shares (np.double): Number of shares traded.
        cost_per_share (np.double): Cost per share of the stock.
        total_cost (np.double): Total cost of the transaction, calculated as shares multiplied by cost per share.
        status (str): Current status of the stock record, defaults to 'pending'.
        notes (Optional[str]): Additional notes or comments about the transaction.

    Methods:
        update_total_cost: Recalculates the total cost of the transaction.
        create_new_uid: Generates a new unique identifier for the stock record.
    
    Notes:
        An instance of this class shall be created without the uid and total_cost attributes 
        as they are automatically generated with the creation of an insatnce.
    """
    uid: str = field(init=False)
    timestamp: datetime = field(init=False, default=datetime.now())
    symbol: str 
    side: Literal["buy", "sell"]
    order_type: Literal["market", "limit", "stop", "stop_limit"]
    shares: np.double 
    cost_per_share: np.double
    total_cost: np.double = field(init=False)
    status: str = field(default=Statuses.pending.value)
    notes: Optional[str] = None

    def __post_init__(self):
        """ Calculates the total cost after the stock record is initialized. """
        self.update_total_cost()
        self.uid = generate_uuid()

    def create_new_uid(self):
        self.uid = generate_uuid()
    
    def update_total_cost(self):
        self.total_cost = np.double(self.shares * self.cost_per_share)

    @classmethod
    def from_tuple(cls, data_tuple: Tuple) -> 'BetterDataclass':
        """
        Creates an instance of StockRecord from a tuple that does not include a UID.

        This method is useful when the tuple data from an external source does not contain a unique identifier
        and one needs to be generated or assigned later. It assumes the tuple contains all necessary data except the UID,
        which will be set to None initially.

        Args:
            data_tuple (Tuple): A tuple containing all necessary fields for StockRecord except the UID. 
                                Expected order should correspond to the dataclass fields starting from 'timestamp'.

        Returns:
            StockRecord: An instance of StockRecord with the 'uid' field set to None, and other attributes initialized from the tuple.
        """
        # Instantiate the object without calling the __init__ or __post_init__
        instance = cls.__new__(cls)

        # Assign all attributes directly from the tuple to the instance
        for field, value in zip(fields(cls), data_tuple):
            setattr(instance, field.name, value)

        # Recalculate any dependent fields if necessary
        instance.__post_init__()

        return instance
    
    @classmethod
    def from_uidless_tuple(cls, data_tuple: Tuple) -> 'StockRecord':
        """
        Converts a tuple containing ALL the necessary fields to 
        a dataclass instance except the first one - the UID
        """
        # Instantiate the object without calling the __init__ or __post_init__
        instance = cls.__new__(cls)

        # Assign all attributes directly from the tuple to the instance
        setattr(instance, "uid", None)
        for field, value in zip(fields(cls)[1:], data_tuple):
            setattr(instance, field.name, value)
        
        return instance

# Server Response
@dataclass
class ServerResponse(BetterDataclass):
    """
    Standard format for the server responses, encapsulating the success or failure of an operation along with associated data.

    Attributes:
        success (bool): Indicates whether the operation was successful.
        error (str): Descriptive error message if the operation failed.
        data (str): Data payload returned by the server if the operation was successful.
        debug (str): Debugging information.
        extra (str): Additional information.

    Methods:
        reset: Resets all attributes to their default values, typically used when an error occurs.
    """
    success: bool = False
    error: str = ""
    data: str = ""
    debug: str = ""
    extra: str = ""

    def reset(self) -> None:
        self.success = False
        self.error = ""
        self.data = ""
        self.debug = ""
        self.extra = ""

# User Identifiers
class UserIdentifiers(Enum):
    """
    Enumeration of user identifier keys used in the Userbase database, simplifying the access to user-related fields.

    Attributes:
        uuid (str): Unique identifier for a user.
        email (str): Email address of the user.
        username (str): Username of the user.
        password (str): Password of the user.
        balance (str): Financial balance of the user.
    """
    uuid = "uuid"
    email = "email"
    username = "username"
    password = "password"
    balance = "balance"

    @classmethod
    def __contains__(cls, item):
        return item in (member.value for member in cls)