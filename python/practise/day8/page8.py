# implement the banking system
# - bank can add one or more customers
# - customer should be able to open account
# - customer should be able to perform the operations
#   like deposit, withdraw, check balance
# - customer can close his/her account
# - requirements
#   - there should be a class named Bank which will maintain
#     a list of customer accounts
#   - there should be a customer's account class which should contain
#     1. deposit
#     2. withdraw
#     3. balance check 
#   - there should be derived classes of account
#    - SavingAccount, CurrentAccount and Fixed Deposit
#   - customer has multiple accounts

class Customer:
    def __init__(self, customer_id, name, address, phone, email):
        self.__customer_id = customer_id
        self.__name = name
        self.__address = address
        self.__phone = phone
        self.__email = email
        # customer may have multiple accounts
        self.__accounts = []

    def open_account(self, account_id, amount, account_type):
        if account_type == 'savings':
            account = SavingsAccount(account_id, amount)
            self.__accounts.append(account) 
        elif account_type  == 'fd':
            account = FDAccount(account_id, amount)
            self.__accounts.append(account)
        else:
            print("invalid account type")

    def show_all_accounts(self):
        for account in self.__accounts:
            account.check_balance()
    def get_customer_id(self):
        return self.__customer_id
    def get_new_account_id(self):
        return len(self.__accounts) + 1

class Account:
    def __init__(self, account_id, balance_amount):
        self._account_id = account_id
        self._balance_amount = balance_amount

    def check_balance(self):
        print(f"current balance in {self._account_id} = {self._balance_amount}")    

class SavingsAccount(Account):
    def __init__(self, account_id, amount):
        super().__init__(account_id, amount)

    def deposit(self, amount):
        # add the amount to current balance
        self._balance_amount += amount

    def withdraw(self, amount):
        if amount < self._balance_amount:
            self._balance_amount -= amount
        else:
            print(f"amount should be less than {self._balance_amount}")    

class FDAccount(Account):
    pass

class Bank:
    def __init__(self, name, address):
        self.__name = name
        self.__address = address

        # bank may have multiple cutomers
        self.__customers = []

    def add_customer(self, name, address, phone, email):
        customer_id = len(self.__customers) + 1
        customer = Customer(customer_id, name, address, phone, email)
        self.__customers.append(customer)
        return customer_id

    def open_new_account(self, customer_id, account_type, amount):
        # find the customer object using the id
        for customer in self.__customers:
            if customer.get_customer_id() == customer_id:
                # add a new account to customer's object
                account_id = customer.get_new_account_id()
                customer.open_account(account_id, amount, account_type)
                break
            else:
                print("this customer does not exist")

    def show_all_accounts_of_customer(self, customer_id):
        for customer in self.__customers:
                        if customer.get_customer_id() == customer_id:
                            customer.show_all_accounts()
                            break
                        else:
                            print("customer does not exist")

bank = Bank('bank of Germany', 'Germany')
cid = bank.add_customer('soham', 'germany', '9096100340', 'sk@gmail.com')
bank.open_new_account(cid, 'savings', 1000)
bank.open_new_account(cid, 'fd', 5000)
bank.show_all_accounts_of_customer(cid)                            

        

        