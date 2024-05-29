from typing import Union
import copy 

from sqlalchemy import update
from sqlalchemy.orm.session import Session
import numpy as np

# Modules
from utils.logger_script import logger
from utils.yfinance_helper import get_symbol_info

from records.records import StockRecord, Statuses, UserIdentifiers

from data.database import DatabasesNames
from data.userbase.model import Userbase
from data.utils.get_databases import get_db
from data.utils.get_databases import get_table_object_from_selected_database_by_name
from data.dynamic_databases.helper import add_stock_data_to_selected_database_table, remove_row_by_uid, get_user_shares_by_symbol
from data.userbase.helper import get_user_from_userbase


class StockHandler:
    def __init__(self):
        self.status = ""

    def deal_with_transaction(self, stock_record: StockRecord, uuid: str):
        """
        Processes a stock transaction for a given user identified by UUID. This involves checking the user's balance,
        updating their portfolio, and logging the transaction. The method handles both buying and selling of shares.
        
        Args:
            stock_record (StockRecord): An instance of StockRecord that contains details about the transaction such as
                                        the number of shares, the cost per share, and whether the transaction is a buy or sell.
            uuid (str): The unique identifier for a user in the userbase.

        Returns:
            None: This method updates the database directly and sets the class variable 'status' with the result of the transaction.
                It does not return any value but logs errors or success messages directly.

        Raises:
            Exception: If there are issues converting the stock record to a dictionary or if the database operations fail,
                        an exception is logged and the status is updated to 'Internal Server Error'.

        Notes:
            This method uses transactions to ensure all database operations are completed successfully before committing the changes.
            It also handles partial transactions where a user may not have enough funds to buy the intended number of shares or
            there are not enough shares available to sell.
        """
        saved_user: Union[Userbase, None] = get_user_from_userbase(identifier=UserIdentifiers.uuid.value, value=uuid)

        if saved_user is None:
            logger.error(f"Could not retrieve user from userbase")
            self.status = "Internal Server Error"
            return

        user_balance = saved_user.balance

        if stock_record.side == "buy":
            if user_balance >= stock_record.total_cost:                
                # Update transaction to be tracked
                stock_record.status = Statuses.tracked.value
                # Output stock record to dict
                try:
                    stock_record_dict = stock_record.to_dict()
                except Exception as error:
                    logger.error(f"Could not output stock record into a dictionary. Error: {error}")
                    self.status = "Internal Server Error"
                    return 
                success_transactions = add_stock_data_to_selected_database_table(
                    database_name=DatabasesNames.transactions.value,
                    table_name=uuid,
                    stock_data=stock_record_dict
                )
                success_portfolio = add_stock_data_to_selected_database_table(
                    database_name=DatabasesNames.portfolios.value,
                    table_name=uuid,
                    stock_data=stock_record_dict
                )

                if success_transactions and success_portfolio:
                    logger.debug(f"Successfully added transaction to transaction history and active portfolio of user {uuid}")
                    status = f"Successfully bought {int(stock_record.shares * 100) / 100} shares, each for {stock_record.cost_per_share} and in total {int(stock_record.total_cost * 100) / 100}"
                    logger.info(f"{uuid} {status}")
                    self.status = status
                    # Remove cost of shares from user's balance
                    user_balance -= stock_record.total_cost
                else:
                    logger.error(f"Transaction from user {uuid} was not succcessful")
                    self.status = "Internal Server Error"
            else:
                # Sell the amount of stocks the user can buy
                logger.warning(f"User {uuid} doesn't have enough money to buy {stock_record.shares} shares of {stock_record.symbol}. \
                               As they cost {stock_record.total_cost} and the user only has {user_balance}")
                max_shares = np.double(user_balance / stock_record.cost_per_share)
                logger.error(f"max shares: {max_shares}")
                
                if max_shares > 0:
                    stock_record.shares = max_shares
                    stock_record.update_total_cost()
                    logger.error(f"calling again")
                    self.deal_with_transaction(stock_record, uuid)
                    return
                else:
                    logger.warning(f"The user doesn't have enough money to buy any amount of shares")
                    self.status = "Insufficient funds"
        elif stock_record.side == "sell":      
            # Get the portfolio's table object for querying
            table_object = get_table_object_from_selected_database_by_name(table_name=uuid, database_name=DatabasesNames.transactions.value)

            if table_object is None:
                logger.error(f"Could not retrieve portfolio table object")
                return

            if stock_record.shares <= 0:
                logger.warning(f"Transaction from user {uuid} attempted to sell 0 or fewer shares")
                self.status = "Cannot buy 0 or fewer shares"
                return
            
            # Sell the shares of the symbol form the portfolio
            revenue, unsold_shares = self.sell_shares(uuid=uuid, symbol=stock_record.symbol, shares=stock_record.shares)

            # Add to user balance
            user_balance += revenue
 
            stock_record.shares -= unsold_shares
            stock_record.status = Statuses.archived.value

            try:
                stock_record_dict = stock_record.to_dict()
            except Exception as error:
                logger.error(f"Could not output stock record into a dictionary. Error: {error}")
            
            flag = add_stock_data_to_selected_database_table(
                database_name=DatabasesNames.transactions.value,
                table_name=uuid,
                stock_data=stock_record_dict
            )
            if flag:
                status = f"Successully sold {stock_record.shares} shares for a revenue of {int(revenue * 100) / 100}. Each share for a price of {int(stock_record.cost_per_share * 100) / 100}"
                logger.info(status)
                self.status = status
            else:
                logger.info(f"Failed to update transactions database with the sell transaction data")
                self.status = "Could not sell shares. Internal Server Error"
        

        # Update user balance 
        session: Session = next(get_db(DatabasesNames.userbase.value))
        session.execute(
            update(Userbase).
            where(Userbase.uuid == uuid).
            values(balance=user_balance)
        )
        session.commit() 
        session.close()
            
    def sell_shares(self, uuid: str, symbol: str, shares: np.double) -> np.double:
        """
        Handles the selling of shares from a user's portfolio. It fetches the user's shares from the database,
        calculates the potential revenue based on current market prices, and updates the user's portfolio.

        Args:
            uuid (str): The unique identifier of the user who is selling the shares.
            symbol (str): The stock symbol for which shares are being sold.
            shares (np.double): The number of shares to sell.

        Returns:
            Tuple[np.double, np.double]: A tuple containing two elements:
                - Revenue generated from the sold shares.
                - The number of shares that could not be sold (if any).
        """
        shares_to_sell = copy.copy(shares)
        if shares_to_sell <= 0:
            logger.warning("Attempted to sell zero or fewer shares.")
            return (0, shares)

        # Fetch the current market price for the symbol
        symbol_info = get_symbol_info(symbol)
        if not symbol_info or 'bid' not in symbol_info:
            logger.error("Failed to fetch current market price.")
            return (0, shares)

        current_price = symbol_info['bid']

        portfolio_session: Session = next(get_db(DatabasesNames.portfolios.value))
        transaction_session: Session = next(get_db(DatabasesNames.transactions.value))

        try:
            shares_list = get_user_shares_by_symbol(DatabasesNames.portfolios.value, uuid, symbol, include_uid=True)
            total_shares = sum([entry['shares'] for entry in shares_list])

            revenue = 0

            # Sort transactions by lowest cost per share when bought
            shares_list.sort(key=lambda x: abs(x['cost_per_share']))

            table_object_portfolios = get_table_object_from_selected_database_by_name(table_name=uuid, database_name=DatabasesNames.portfolios.value)
            table_object_transactions = get_table_object_from_selected_database_by_name(table_name=uuid, database_name=DatabasesNames.transactions.value)

            rows_uids_to_remove = []
            for entry in shares_list:
                uid = entry['uid']
                shares = entry['shares']
                if shares_to_sell <= 0:
                    logger.debug(f"Done selling all shares")
                    break

                shares_to_reduce = min(shares, shares_to_sell)
                revenue += shares_to_reduce * current_price
                shares_to_sell -= shares_to_reduce

                # Update the shares count in the database
                new_share_count = shares - shares_to_reduce
                if new_share_count > 0:
                    update_stmt = update(table_object_portfolios).where(table_object_portfolios.c.uid == uid).values(shares=new_share_count)
                    portfolio_session.execute(update_stmt)
                    logger.info(f"Reduced {shares_to_reduce} shares from UID {uid} in transaction.")
                else:
                    # Archive the transaction if no shares remain
                    archive_stmt = update(table_object_transactions).where(table_object_transactions.c.uid == uid).values(status=Statuses.archived.value)
                    transaction_session.execute(archive_stmt)
                    logger.info(f"Transaction UID {uid} archived as all shares are sold. {shares}")

                    rows_uids_to_remove.append(uid)

            portfolio_session.commit()
            transaction_session.commit()
            
            for row_uid in rows_uids_to_remove:
                remove_row_by_uid(DatabasesNames.portfolios.value, uuid, row_uid)

            if shares_to_sell > 0:
                logger.warning(f"Not all shares could be sold; {shares_to_sell} shares remain unsold.")

            return revenue, shares_to_sell
        except Exception as error:
            import traceback
            portfolio_session.rollback()
            transaction_session.rollback()
            logger.error(f"Error while trying to sell shares for user {uuid}: {error}")
            logger.error(traceback.format_exc())
            return (0,shares)
        finally:
            portfolio_session.close()
            transaction_session.close()


# for scheduler example see previous commits for a function that was here