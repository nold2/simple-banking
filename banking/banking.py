import random
import sqlite3


class Database:
    DATABASE_NAME = "card.s3db"
    TABLE_NAME = "card"

    def __init__(self):
        self.conn = sqlite3.connect(self.DATABASE_NAME)
        self.cur = self.conn.cursor()

        self.cur.execute(
            f"""
                DROP TABLE {self.TABLE_NAME};
            """
        )

        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
                CONSTRAINT test_positive_balance CHECK (balance >= 0)
            );
            """
        )
        self.conn.commit()

    def create_account(self, card_number, pin):
        self.cur.execute(
            f"""
                INSERT INTO {self.TABLE_NAME} (number, pin, balance) VALUES({card_number}, {pin}, 0)
            """
        )
        self.conn.commit()

    def add_income(self, account, income):
        self.cur.execute(
            f"""
                UPDATE {self.TABLE_NAME} SET balance = balance + {income} WHERE number = {account}
            """
        )
        self.conn.commit()

    def authenticate(self, card_number, pin):
        try:
            account, *_ = self.cur \
                .execute(f'SELECT * FROM "{self.TABLE_NAME}" WHERE number = {card_number} AND pin = {pin}') \
                .fetchall()
            bank_id, card, pin, balance = account
            return {
                "id": bank_id,
                "card": card,
                "pin": pin,
                "balance": balance,
                "Error": False
            }
        except ValueError:
            return {
                "Error": True
            }

    def is_account_exists(self, card_number):
        try:
            account, *_ = self.cur.execute(
                f'SELECT id, number FROM {self.TABLE_NAME} WHERE number = {card_number}').fetchall()
            bank_id, card = account
            return {
                "id": bank_id,
                "card": card
            }
        except ValueError:
            return {
                "Error": True
            }

    def transfer(self, transferer, transferee, amount):
        try:
            print(self.cur.execute(f"SELECT balance, number FROM {self.TABLE_NAME}").fetchall())
            print(f"amount: {amount}")
            self.cur.execute(
                f"""
                    UPDATE {self.TABLE_NAME} SET balance = balance - {amount} WHERE number = {transferer}
                """
            )
            self.conn.commit()

            self.cur.execute(
                f"""
                    UPDATE {self.TABLE_NAME} SET balance = balance + {amount} WHERE number = {transferee}
                """
            )
            self.conn.commit()
            return {
                "Error": False
            }
        except sqlite3.IntegrityError:
            return {
                "Error": True
            }

    def close_account(self, account):
        self.cur.execute(
            f"""
                DELETE FROM {self.TABLE_NAME} WHERE number = {account}
            """
        )
        self.conn.commit()


database = Database()


class Router:
    REGISTER = "register"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    BALANCE = "balance"
    ADD_INCOME = "add_income"
    CARD_INVALID = "CARD_INVALID"
    CARD_DOES_NOT_EXISTS = "CARD_DOES_NOT_EXISTS"
    TRANSFER_FAILED = "TRANSFER_FAILED"
    TRANSFER_SUCCEED = "TRANSFER_SUCCEED"
    CLOSE_ACCOUNT = "CLOSE_ACCOUNT"
    EXIT = "exit"


class Menu:
    def __init__(self):
        self.options = {}
        self.selected = None

    def show(self):
        [print(f"{key}. {value}") for key, value in self.options.items()]

    def select(self, choice):
        self.selected = choice

    def process(self):
        pass


class HomeMenu(Menu):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.options = {
            "1": "Create an account",
            "2": "Log into account",
            "0": "Exit"
        }

    def register(self):
        return Router.REGISTER, self.auth.register(bank=Bank(db=database))

    def login(self):
        card_input = input("Enter your card number:\n")
        pin_input = input("Enter your PIN:\n")

        res = self.auth.login(card_input=card_input, pin_input=pin_input)

        return Router.LOGIN_SUCCESS if res else Router.LOGIN_FAILED, None

    def logout(self):
        return Router.LOGOUT, self.auth.logout()

    def process(self):
        if self.selected == "1":
            return self.register()

        elif self.selected == "2":
            return self.login()

        elif self.selected == "0":
            return self.logout()


class BankMenu(Menu):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.options = {
            "1": "Balance",
            "2": "Add income",
            "3": "Do transfer",
            "4": "Close account",
            "5": "Log out",
            "0": "Exit",
        }

    @property
    def bank(self):
        return self.auth.logged_in

    def get_balance(self):
        return Router.BALANCE, self.bank.get_balance()

    def add_income(self):
        income = input("Enter income:")
        return Router.ADD_INCOME, self.bank.add_income(income)

    def transfer(self):
        card = input("Enter card number:")
        if not is_checksum_valid(card):
            return Router.CARD_INVALID, None
        if self.auth.database.is_account_exists(card_number=card).get("Error"):
            return Router.CARD_DOES_NOT_EXISTS, None

        amount = input("Enter how much you want to transfer:")
        res = self.bank.transfer(transferee=card, amount=amount)

        if res.get("Error"):
            return Router.TRANSFER_FAILED, None

        return Router.TRANSFER_SUCCEED, None

    def close_account(self):
        self.bank.close_account()
        return Router.CLOSE_ACCOUNT, None

    def logout(self):
        return Router.LOGOUT, None

    def exit(self):
        return Router.EXIT, None

    def process(self):
        if self.selected == "1":
            return self.get_balance()
        elif self.selected == "2":
            return self.add_income()
        elif self.selected == "3":
            return self.transfer()
        elif self.selected == "4":
            return self.close_account()
        elif self.selected == "5":
            return self.logout()
        elif self.selected == "0":
            return self.exit()


def generate_luhn_number(card_number):
    to_list_of_numbers = [int(value) for value in card_number]
    multiply_odd_index_by_two = [value * 2 if (index + 1) % 2 == 1 else value for index, value in
                                 enumerate(to_list_of_numbers)]
    ensure_all_value_under_nine = [value if value <= 9 else value - 9 for value in multiply_odd_index_by_two]
    return sum(ensure_all_value_under_nine)


def is_checksum_valid(card_number):
    return generate_luhn_number(card_number) % 10 == 0


def generate_card_number():
    initial_number = f"400000{str(random.randint(000000000, 999999999)).zfill(9)}"
    checksum = 0 if is_checksum_valid(initial_number) else 10 - (generate_luhn_number(initial_number) % 10)
    to_list_of_numbers = [int(value) for value in initial_number]
    to_list_of_numbers.append(checksum)
    return "".join([str(value) for value in to_list_of_numbers])


class Bank:
    def __init__(self, db):
        self.__card_number = generate_card_number()
        self.__pin = str(random.randrange(0000, 9999)).zfill(4)
        self.__balance = 0
        self.database = db

    def get_card_number(self):
        return self.__card_number

    def get_pin(self):
        return self.__pin

    def get_balance(self):
        return self.__balance

    def add_income(self, income):
        self.database.add_income(self.get_card_number(), income)
        self.__balance += int(income)
        return None

    def is_account_exists(self, account):
        return self.database.is_account_exists(account)

    def transfer(self, transferee, amount):
        return self.database.transfer(transferer=self.get_card_number(), transferee=transferee, amount=amount)

    def close_account(self):
        return self.database.close_account(account=self.get_card_number())


class Auth:
    def __init__(self, db):
        self.banks = []
        self.database = db
        self.logged_in = None

    def register(self, bank):
        self.banks.append(bank)
        res = {"card": bank.get_card_number(), "pin": bank.get_pin()}
        self.database.create_account(card_number=res.get("card"), pin=res.get("pin"))
        return res

    def login(self, card_input, pin_input):
        res = self.database.authenticate(card_number=card_input, pin=pin_input)
        for bank in self.banks:
            if bank.get_card_number() == res.get("card"):
                self.logged_in = bank
        return not res.get("Error")

    def logout(self):
        self.banks = None
        return None


def main():
    auth = Auth(db=database)

    home_menu = HomeMenu(auth=auth)
    bank_menu = BankMenu(auth=auth)
    while True:
        home_menu.show()
        home_menu.select(choice=input())
        action, data = home_menu.process()

        if action == Router.REGISTER:
            print(
                f"Your card has been created\nYour card number:\n{data.get('card')}\nYour card PIN:\n{data.get('pin')}\n")
            continue
        elif action == Router.LOGIN_FAILED:
            print("Wrong card number or PIN!")
            continue
        elif action == Router.LOGIN_SUCCESS:
            print("\nYou have successfully logged in!")
            while True:
                bank_menu.show()
                bank_menu.select(choice=input())
                action, data = bank_menu.process()

                if action == Router.BALANCE:
                    print("\nBalance: ", data)
                elif action == Router.LOGOUT:
                    print("\nYou have successfully logged out!")
                    continue
                elif action == Router.CARD_INVALID:
                    print("\nProbably you made a mistake in the card number.\nPlease try again!")
                    continue
                elif action == Router.CARD_DOES_NOT_EXISTS:
                    print("\nSuch a card does not exist.")
                    continue
                elif action == Router.ADD_INCOME:
                    print("\nIncome was added!")
                elif action == Router.TRANSFER_FAILED:
                    print("\nNot enough Money!")
                elif action == Router.TRANSFER_SUCCEED:
                    print("\nSuccess!")
                elif action == Router.CLOSE_ACCOUNT:
                    print("\nThe account has been closed!")
                else:
                    exit()
        else:
            print("Bye!")
            exit()


# main()
