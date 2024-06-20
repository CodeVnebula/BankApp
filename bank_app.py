import json
import random
import hashlib
from datetime import date, datetime, timedelta
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
import textwrap
from typing import Tuple
import socket

class Internet():
    def is_connected(host="8.8.8.8", port=53, timeout=3):
        """
        Checks if the computer is connected to the internet.
        
        Parameters:
        host (str): The host to connect to. Default is Google's DNS server.
        port (int): The port to connect to. Default is 53.
        timeout (int): The connection timeout duration. Default is 3 seconds.

        Returns:
        bool: True if the computer is connected to the internet, False otherwise.
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except OSError:
            return False
        

class Email():
    def __init__(self, email_account_to: str) -> None:
        self.bank_email, self.password = self.get_bank_email()
        self.email_account_to = email_account_to
        
    
    def send_email(self, subject: str, email_body: str) -> Tuple[bool, str]:
        if not Internet.is_connected():
            return False, "It seems you are not connected to internet or your connection is poor. Please try again when connection is back!"
        
        if not Validation.is_valid_email(self.email_account_to):
            return False, "Oops! It seems the email you entered is invalid. Please double-check and try again."
        
        email = MIMEMultipart()
        email["From"] = self.bank_email
        email["To"] = self.email_account_to
        email["Subject"] = subject
        
        email.attach(MIMEText(email_body, "plain"))

        context = ssl.create_default_context()
        
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(self.bank_email, self.password)
                smtp.sendmail(self.bank_email, self.email_account_to, email.as_string())
                return True, "Email sent successfully"
        except smtplib.SMTPAuthenticationError as e:
            return False, "Failed to authenticate with the SMTP server:", e
        except smtplib.SMTPRecipientsRefused as e:
            return False, "All recipient addresses were refused:", e
        except smtplib.SMTPSenderRefused as e:
            return False, "The sender address was refused:", e
        except smtplib.SMTPDataError as e:
            return False, "The SMTP server replied with an unexpected error code:", e
        except smtplib.SMTPConnectError as e:
            return False, "Failed to connect to the SMTP server:", e
        except smtplib.SMTPHeloError as e:
            return False, "The server refused our HELO message:", e
        except smtplib.SMTPNotSupportedError as e:
            return False, "The SMTP server does not support the STARTTLS extension:", e
        except smtplib.SMTPException as e:
            return False, "An error occurred during the SMTP transaction:", e
        except Exception as e:
            return False, "An unexpected error occurred:", e


    @staticmethod
    def get_bank_email() -> Tuple[str, str] | Tuple[bool, str]:
        try:
            with open("bank_email_and_passcode.txt", "r") as bank_email:
                email, password = bank_email.readlines()
                return email, password
        except FileNotFoundError as e:
            return False, "Couldn't find the bank email information", e
    
    
    @staticmethod
    def verification_code() -> str:
        return str(random.randint(100000, 999999))
    
    

class User():
    def __init__(self, first_name: str, last_name: str, personal_id: str, phone_number: str, email: str, password: str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.personal_id = personal_id
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.account_number = Functionalities.generate_account_number()
        self.pin_code = Functionalities.generate_pin_code()
        self.account_creation_date = Functionalities.current_date()
        self.file_path = "Data/accountsData.json"
    
    
    def create_bank_account(self) -> Tuple[bool, str] | Tuple[str, str]:
        if not Validation.is_valid_name_surname(self.first_name):
            error_message = "Oops! It seems like the first name you entered doesn't meet our requirements. Please try a valid first name."
            return False, error_message

        if not Validation.is_valid_name_surname(self.last_name):
            error_message = "Oops! It seems like the last name you entered doesn't meet our requirements. Please try a valid last name."
            return False, error_message
        
        if not Validation.is_valid_email(self.email):
            error_message = "Oops! It seems the email you entered is invalid. Please double-check and try again."
            return False, error_message
        
        if not Validation.is_valid_personal_id(self.personal_id):
            error_message = "Oops! It seems the personal ID you entered is invalid. Please double-check and try again."
            return False, error_message
        
        if not Validation.is_valid_phone_number(self.phone_number):
            error_message = "Oops! It seems like phone number you entered is invalid or doesn't meet our requirements. Please double-check and try again."
            return False, error_message
        
        if not Validation.is_valid_password(self.password):
            error_message = "Oops! It seems like password you entered doesn't meet our requirements. Please double-check and try again."
            return False, error_message

        data = JsonFileTasks(self.file_path).load_data()
        
        if len(data) == 0:
            data[self.personal_id] = {
                "first_name" : self.first_name,
                "last_name" : self.last_name,
                "phone_number" : self.phone_number,
                "email" : self.email,
                "password" : self.hash_password(self.password),
                "pin_code" : self.pin_code,
                "account_number" : self.account_number,
                "account_creation_date" : str(self.account_creation_date),
                "balance" : 0.0,
                "withdrawal_disabled_date" : "",
                "pin_code_changed_manually" : False
            }
            
        else:
            if self.personal_id in data:
                error_message = "Oops! It seems the personal ID you entered or already registered. Please double-check and try again."
                return False, error_message
            
            for info in data.values():
                if info["email"] == self.email:
                    error_message = "Opps! It seems the email you entered is already registered. Please double-check and try again."
                    return False, error_message
            
                if info["phone_number"] == self.phone_number:
                    error_message = "Opps! It seems the phone number you entered is already registered. Please double-check and try again."
                    return False, error_message
            
            for info in data.values():
                if info["account_number"] != self.account_number:
                    break
                else:
                    self.account_number = Functionalities.generate_account_number()
            
            data[self.personal_id] = {
                "first_name" : self.first_name,
                "last_name" : self.last_name,
                "phone_number" : self.phone_number,
                "email" : self.email,
                "password" : self.hash_password(self.password),
                "pin_code" : self.pin_code,
                "account_number" : self.account_number,
                "account_creation_date" : str(self.account_creation_date),
                "balance" : 0.0,
                "withdrawal_disabled_date" : "",
                "pin_code_changed_manually" : False
            } 

        JsonFileTasks(self.file_path).save_data(data)
        return self.pin_code, self.account_number
     
       
    def login_verification(self, email: str, password: str) -> Tuple[bool, str]:
        users = JsonFileTasks(self.file_path).load_data()
        account_found = False
        for user in users.values():
            if user['email'] == email and user['password'] == self.hash_password(password):
                return True, "Successfull login"
            if user['email'] == email:
                account_found = True
            
        if account_found == False:
            return False, "It seems the account doesn't exist, try creating one before login"
                
        return False, "Invalid password. Please try again."
    
   
    def hash_password(self, password: str) -> str:
        # sha256 function for hashing input, func returns str
        return hashlib.sha256(password.encode()).hexdigest()
 

    def get_user_details(self, email: str) -> dict:
        data = JsonFileTasks(self.file_path).load_data()

        for personal_id, details in data.items():
            if details["email"] == email:
                personal_info = data[personal_id]
    
        return personal_info
    
    
    def change_password(self, new_password: str) -> Tuple[bool, str]:
        if not Validation.is_valid_password(new_password):
            error_message = "Oops! It seems like password you entered doesn't meet our requirements. Please double-check and try again."
            return False, error_message
        data = JsonFileTasks(self.file_path).load_data()
        if Validation.is_valid_email(self.email):
            for personal_id, details in data.items():
                    if details["email"] == self.email:
                        personal_id = personal_id
                        break
            data[personal_id]["password"] = self.hash_password(new_password)
            JsonFileTasks(self.file_path).save_data(data)
            return True, "Password successfully changed"
        return False, "Something went wrong"
    
    
    def change_pin_code(self, new_pin_code: str, account_number: str) -> Tuple[bool, str]:
        data = JsonFileTasks(self.file_path).load_data()

        if Validation.is_valid_account_number(account_number):
            for personal_id, details in data.items():
                if details["account_number"] == account_number:
                    personal_id = personal_id
                    break
        
        if Validation.is_valid_email(self.email):
            for personal_id, details in data.items():
                if details["email"] == self.email:
                    personal_id = personal_id
                    break
                
        if data[personal_id]["pin_code_changed_manually"] == True: 
            error_message = "It seems you have already changed PIN code. You can change PIN code only once!"
            return False, error_message
        
        if len(new_pin_code) != 4:
            error_message = "PIN code must be 4 digits in length"
            return False, error_message

        for digit in new_pin_code:
            if not digit.isdigit():
                error_message = "PIN code must contain only digits"
                return False, error_message
        
            data[personal_id]['pin_code'] = new_pin_code
            data[personal_id]["pin_code_changed_manually"] = True
            JsonFileTasks(self.file_path).save_data(data)
            return True, "PIN code successfully changed"
        return False, "Something went wrong"


class Account():
    def __init__(self, account_number: str) -> None:
        self.account_number = account_number
        self.account_history_file_path = "Data/accounts_history.json"
        self.data_file_path = "Data/accountsData.json"
        self.data = JsonFileTasks(self.data_file_path).load_data()
        self.number_of_tries = 0
        
    def get_personal_id_by_account_number(self, acc_number: str) -> str | None:
        if Validation.is_valid_account_number(acc_number):
            for personal_id, details in self.data.items():
                if details["account_number"] == acc_number:
                    return personal_id
            return None

    def deposit(self, amount: str | float | int) -> Tuple[bool, str]:
        try:
            amount = float(amount)
        except ValueError as ve:
            error_message = "Please enter valid amount, Error Msg:" + str(ve)
            return False, error_message
            
        personal_id = self.get_personal_id_by_account_number(self.account_number)
        if not personal_id:
            error_message = "Personal ID Error"
            return False, error_message
        
        if amount <= 0:
            return False, "Insufficient funds"
        
        if amount > 100000:
            return False, "You can not deposit more than 100'000 at once"
        
        self.data[personal_id]["balance"] += amount
        filling_message = f"Balance was filled with {amount}$, Account - {self.account_number}, {Functionalities.current_date()}/{Functionalities.current_time()}."
        
        history = JsonFileTasks(self.account_history_file_path).load_data()

        if self.account_number not in history:
            history[self.account_number] = {
                "balance_filling_history" : [filling_message],
                "transaction_history" : [],
                "withdrawal_history" : []
            }
        
        else:
            filling_history = history[self.account_number]["balance_filling_history"]
            filling_history.append(filling_message)
            
        email_account = self.data[personal_id]["email"]    
        
        email = Email(email_account)
        
        subject = "Balance was filled"
        body = textwrap.dedent(f"""
            Balance was filled with {amount}$, 
            Account - {self.account_number},
            Date: {Functionalities.current_date()}
            Time: {Functionalities.current_time()}
        """)
        
        email.send_email(subject, body)
        
        JsonFileTasks(self.account_history_file_path).save_data(history)
        JsonFileTasks(self.data_file_path).save_data(self.data)
        
        return True, "Successfully filled balance"
        
        
    def withdraw(self, amount: str | float | int, inputted_pin_code: str) -> Tuple[bool, str]:
        try:
            amount = abs(float(amount))
        except ValueError as ve:
            error_message = "Please enter valid amount, Error Msg:" + str(ve)
            return False, error_message
        
        personal_id = self.get_personal_id_by_account_number(self.account_number)
        if not personal_id:
            error_message = "Personal ID Error"
            return False, error_message
        
        if self.data[personal_id]["withdrawal_disabled_date"] == str(Functionalities.current_date()):
            error_message = "It seems you have entered wrong pin code few times, you won't be able to make withdrawal for one day!"
            return False, error_message
        else:
            self.data[personal_id]["withdrawal_disabled_date"] = ""
            JsonFileTasks(self.data_file_path).save_data(self.data)
        
        pin_code = self.data[personal_id]["pin_code"]
        
        if pin_code != inputted_pin_code:
            if self.number_of_tries == 3:
                self.data[personal_id]["withdrawal_disabled_date"] = str(Functionalities.current_date())
                JsonFileTasks(self.data_file_path).save_data(self.data)
                error_message = "It seems you have entered wrong pin code few times, you won't be able to make withdrawal for one day!"
                return False, error_message
            
            self.number_of_tries += 1
            error_message = "It seems pin code you have entered does not match your pin code. Please double-check and try again."
            return False, error_message
        
        balance = self.data[personal_id]["balance"]
        
        if amount > balance:
            return False, "Insufficient funds"
        
        if amount > 5000:
            return False, "You can not withdraw more than 5000$ at once"
        
        balance -= amount
        self.data[personal_id]["balance"] = balance
        
        withdrawal_message = f"Amount withdrawn from the account {amount}$, Account - {self.account_number}, {Functionalities.current_date()}/{Functionalities.current_time()}."
        
        history = JsonFileTasks(self.account_history_file_path).load_data()
        
        if self.account_number not in history:
            history[self.account_number] = {
                "balance_filling_history" : [],
                "transaction_history" : [],
                "withdrawal_history" : [withdrawal_message]
            }
        
        else:
            withdrawal_history = history[self.account_number]["withdrawal_history"]
            withdrawal_history.append(withdrawal_message)
        
        email_account = self.data[personal_id]["email"]
        
        email = Email(email_account)
        
        subject = "Withdrawal"
        body = textwrap.dedent(f"""
            Amount withdrawn from the account {amount}$, 
            Account - {self.account_number}, 
            Date: {Functionalities.current_date()}
            Time: {Functionalities.current_time()}     
        """)
        
        email.send_email(subject, body)
        
        JsonFileTasks(self.account_history_file_path).save_data(history)
        JsonFileTasks(self.data_file_path).save_data(self.data)
        
        return True, "Successfull withdrawal"
    
    
    def transfer(self, amount: str | float | int, account_number_to: str) -> Tuple[bool, str]:
        try:
            amount = abs(float(amount))
        except ValueError as ve:
            error_message = "Please enter valid amount, Error Msg:" + str(ve)
            return False, error_message
        
        if account_number_to == self.account_number:
            error_message = "It seems like account number you entered is your account. Please double-check and try again."
            return False, error_message
            
        personal_id_acc_from = self.get_personal_id_by_account_number(self.account_number)
        personal_id_acc_to = self.get_personal_id_by_account_number(account_number_to)
        
        if not personal_id_acc_from:
            error_message = "Error finding account number"
            return False, error_message
        
        if not personal_id_acc_to:
            error_message = "Error, finding account number to"
            return False, error_message
        
        balance_account_number_from = self.data[personal_id_acc_from]["balance"]
        balance_account_number_to = self.data[personal_id_acc_to]["balance"]
        
        if amount > balance_account_number_from:
            return False, "Insufficient funds"
        
        transfer_message_acc_to = f"Balance was filled with {amount}$, Account - {account_number_to}, from {self.account_number}, {Functionalities.current_date()}/{Functionalities.current_time()}. Sender: {self.data[personal_id_acc_from]["last_name"]} {self.data[personal_id_acc_from]["first_name"]}"
        transfer_message_acc_from = f"Transfer from {self.account_number} to {account_number_to}, Amount: {amount}$, {Functionalities.current_date()}/{Functionalities.current_time()}. Recipient: {self.data[personal_id_acc_to]["last_name"]} {self.data[personal_id_acc_to]["first_name"]}"
        
        balance_account_number_from -= amount
        balance_account_number_to += amount
        
        self.data[personal_id_acc_from]["balance"] = balance_account_number_from
        self.data[personal_id_acc_to]["balance"] = balance_account_number_to
        
        history = JsonFileTasks(self.account_history_file_path).load_data()
        
        if self.account_number not in history:
            history[self.account_number] = {
                "balance_filling_history" : [],
                "transaction_history" : [transfer_message_acc_from],
                "withdrawal_history" : []
            }
        
        else:
            transaction_history = history[self.account_number]["transaction_history"]
            transaction_history.append(transfer_message_acc_from)
        
        
        if account_number_to not in history:
            history[account_number_to] = {
                "balance_filling_history" : [],
                "transaction_history" : [transfer_message_acc_to],
                "withdrawal_history" : []
            }
        
        else:
            transaction_history = history[account_number_to]["transaction_history"]
            transaction_history.append(transfer_message_acc_to)
            
        email_account_from = self.data[personal_id_acc_from]["email"]
        email_account_to = self.data[personal_id_acc_to]["email"]
        
        email_acc_from_instance = Email(email_account_from) 
        email_acc_to_instance = Email(email_account_to)  
        
        subject_email_acc_from = "Transaction made"
        body_email_acc_from = textwrap.dedent(f"""
            Transfer from {self.account_number} to {account_number_to}, 
            Amount: {amount}$, 
            Date: {Functionalities.current_date()}
            Time: {Functionalities.current_time()}. 
            Recipient: {self.data[personal_id_acc_to]["last_name"]} {self.data[personal_id_acc_to]["first_name"]}              
        """) 
        

        subject_email_acc_to = "Balance was filled"
        body_email_acc_to = textwrap.dedent(f"""
            Balance was filled with {amount}$, 
            Account - {account_number_to}, 
            from {self.account_number}, 
            Date: {Functionalities.current_date()}
            Time: {Functionalities.current_time()}. 
            Sender: {self.data[personal_id_acc_from]["last_name"]} {self.data[personal_id_acc_from]["first_name"]}
        """)
        
        email_acc_from_instance.send_email(subject_email_acc_from, body_email_acc_from)
        email_acc_to_instance.send_email(subject_email_acc_to, body_email_acc_to)
        
        JsonFileTasks(self.account_history_file_path).save_data(history)
        JsonFileTasks(self.data_file_path).save_data(self.data)
        
        return True, "Successful transaction!"
    
    
    def get_transaction_history(self) -> list:
        account_history = JsonFileTasks(self.account_history_file_path).load_data()
        return account_history[self.account_number]["transaction_history"]
    
    
    def get_balance_filling_history(self) -> list:
        account_history = JsonFileTasks(self.account_history_file_path).load_data()
        return account_history[self.account_number]["balance_filling_history"]
    
    
    def get_withdrawal_history(self) -> list:
        account_history = JsonFileTasks(self.account_history_file_path).load_data()
        return account_history[self.account_number]["withdrawal_history"]
      
      
class Loan():
    def __init__(self, amount: str | float | int, account_number: str, time_period: str) -> None:
        self.annual_interest_rate = 0.08    # 8%
        self.amount = amount
        self.account_number = account_number
        self.time_period = time_period
        self.loan_data_file_path = "Data/loan_data.json"
        self.data_file_path = "Data/accountsData.json"
        self.history_file_path = "Data/accounts_history.json"
        
    
    def interest_rate(self) -> bool | int | float:
        try:
            self.amount = float(self.amount)
        except ValueError:
            return False
        
        try:
            self.time_period = int(self.time_period)
        except ValueError:
            return False
        
        if (self.amount <= 0 or self.amount > 100000) or (self.time_period < 6 or self.time_period > 48):
            return False
        
        return self.amount * self.annual_interest_rate * (self.time_period / 12)
    
    
    def set_up_loan_details(self) -> Tuple[bool, str]:
        loan_data = JsonFileTasks(self.loan_data_file_path).load_data()
        
        if self.account_number in loan_data and loan_data[self.account_number]["loan_status"] == True:
            error_message = "It seems you have already got an active loan. Please finish it to be able to take a new loan."
            return False, error_message
        
        interest_rate = self.interest_rate()
        
        if interest_rate == False:
            error_message = "It seems details you have entered are wrong! Plase double-check ad try again."
            return False, error_message
        
        interest_rate = float("{:.2f}".format(interest_rate))
        
        account_dets = JsonFileTasks(self.data_file_path).load_data()
        history = JsonFileTasks(self.history_file_path).load_data()
       
        personal_id = Account(self.account_number).get_personal_id_by_account_number(self.account_number)
        
        account_dets[personal_id]["balance"] += self.amount
              
        current_date = Functionalities.current_date()
        last_date = Functionalities.add_months(current_date, self.time_period)
        
        total_repayment = self.amount + interest_rate
        total_repayment = "{:.2f}".format(total_repayment)
       
        min_monthly_payment = float(total_repayment) / self.time_period
        min_monthly_payment = "{:.2f}".format(min_monthly_payment)
        
        loan_message = f"Balance was filled By GB Bank, Account: {self.account_number}. Amount - {self.amount}$, {current_date}. (loan)"
        
        if self.account_number not in history:
            history[self.account_number] = {
                "balance_filling_history" : [loan_message],
                "transaction_history" : [],
                "withdrawal_history" : []
            }
        else:
            history[self.account_number]["balance_filling_history"].append(loan_message)
        
        next_payment_date = Functionalities.add_months(current_date, 1)
        next_payment_date = str(next_payment_date).split(" ")[0]
        
        loan_data[self.account_number] = {
            "loan_approved_date" : str(current_date),
            "loan_expires_date" : str(last_date),
            "time_period" : self.time_period,
            "amount_borrowed" : self.amount,
            "total_repayment" : total_repayment,
            "amount_returned" : 0,
            "amount_left" : total_repayment,
            "interest_rate" : interest_rate,
            "min_monthly_payment" : min_monthly_payment,
            "loan_status" : True,
            "dates_paid" : [],
            "next_payment_date" : next_payment_date,
            "amount_paid_in_current_month" : 0
        }
        
        JsonFileTasks(self.data_file_path).save_data(account_dets)
        JsonFileTasks(self.history_file_path).save_data(history)
        JsonFileTasks(self.loan_data_file_path).save_data(loan_data)
        
        return True, "Loan Successfully approved"
    
    # do u have any imporvements for pay_monthly_loan(self) function?
    
    def pay_monthly_loan(self):
        loan_data = JsonFileTasks(self.loan_data_file_path).load_data()
        
        if self.account_number not in loan_data:
            error_message = "It seems you have not got an active loan. Please double check details and try again later."
            return False, error_message
        
        if loan_data[self.account_number]["loan_status"] == False:
            return False, "It seems your loan is not active anymore."
        
        try:
            self.amount = float(self.amount)
        except ValueError:
            return False, "It seems amount you entered is not valid. Please double check and try again."
        
        min_monthly_payment = float(loan_data[self.account_number]["min_monthly_payment"])
        amount_paid_in_current_month = float(loan_data[self.account_number]["amount_paid_in_current_month"])
        
        account_details = JsonFileTasks(self.data_file_path).load_data()
        personal_id = Account(self.account_number).get_personal_id_by_account_number(self.account_number)
        
        if self.amount >= float(loan_data[self.account_number]["amount_left"]):
            if account_details[personal_id]["balance"] < self.amount:
                return False, "It seems you don't have enough balance. Fill it before trying."
        
            account_details[personal_id]["balance"] -= float(loan_data[self.account_number]["amount_left"])
            
            loan_data[self.account_number]["loan_status"] = False
            loan_data[self.account_number]["dates_paid"].append({str(Functionalities.current_date()) : f"{float(loan_data[self.account_number]["amount_left"])}$"})
            loan_data[self.account_number]["amount_left"] = 0
            loan_data[self.account_number]["amount_returned"] = loan_data[self.account_number]["total_repayment"]
            JsonFileTasks(self.loan_data_file_path).save_data(loan_data)
            JsonFileTasks(self.data_file_path).save_data(account_details)
            return True, "You finished paying for your loan."
            
        if float(loan_data[self.account_number]["amount_left"]) == 0:
            loan_data[self.account_number]["loan_status"] = False
            loan_data[self.account_number]["next_payment_date"] = "--/--/--"
            JsonFileTasks(self.loan_data_file_path).save_data(loan_data)
            JsonFileTasks(self.data_file_path).save_data(account_details)
            return True, "You finished paying for your loan."
        
        if account_details[personal_id]["balance"] < self.amount:
            return False, "It seems you don't have enough balance. Fill it before trying."
        
        current_date = str(Functionalities.current_date())
        next_payment_date = loan_data[self.account_number]["next_payment_date"]
        bigger_date = Functionalities.compare_dates(current_date, next_payment_date)
        
        if bigger_date == 1: 
            if amount_paid_in_current_month < min_monthly_payment:
                loan_data[self.account_number]["amount_left"] = str(float(loan_data[self.account_number]["amount_left"]) + (0.1 * min_monthly_payment))
            
                subject = "Loan payment"
                body = textwrap.dedent(f"""
                    It seems you have not paid the minimum monthly payment for your loan in last month.
                    because of that we have added 10% of the minimum monthly payment to total amount you 
                    have to pay.
                    
                    Please try not to be late next time.
                    
                    GB Bank """
                )
                email = Email(account_details[personal_id]["email"])
                email.send_email(subject, body)
            loan_data[self.account_number]["next_payment_date"] = str(Functionalities.add_months(next_payment_date, 1))
            
            loan_data[self.account_number]["amount_paid_in_current_month"] = 0
            return self.payment_task(account_details, personal_id, loan_data)
            
        return self.payment_task(account_details, personal_id, loan_data)
        
        
    def payment_task(self, account_details, personal_id, loan_data):
        account_details[personal_id]["balance"] -= self.amount
        loan_data[self.account_number]["amount_returned"] += self.amount
        amount_left_to_pay = float(loan_data[self.account_number]["amount_left"]) - self.amount
        loan_data[self.account_number]["amount_left"] = str(amount_left_to_pay)
        loan_data[self.account_number]["amount_paid_in_current_month"] += self.amount
        loan_data[self.account_number]["dates_paid"].append({str(Functionalities.current_date()) : f"{self.amount}$"})
        JsonFileTasks(self.data_file_path).save_data(account_details)
        JsonFileTasks(self.loan_data_file_path).save_data(loan_data)
        return True, "You successfully paid for your loan."
    
    def check_loan_details(self) -> dict:
        loan_details = JsonFileTasks(self.loan_data_file_path).load_data()
        if self.account_number in loan_details and loan_details != None:
            return loan_details[self.account_number]
    
        
    def get_loan_payment_dates(self) -> list:
        loan_details = JsonFileTasks(self.loan_data_file_path).load_data()
        if self.account_number in loan_details and loan_details != None:
            return loan_details[self.account_number]["dates_paid"]

class Validation():
    
    def is_valid_name_surname(name_or_surname: str) -> bool:
        # lets say name cant be longer than 15 chars and less then 2 chars, cant contain spaces, 
        # cant have spaces around, cant contain digits
        
        name_or_surname = name_or_surname.strip()
        length = len(name_or_surname)
        
        if length < 2 or length > 15:
            return False
        
        if " " in name_or_surname:
            return False
        
        for char in name_or_surname:
            if char.isdigit():
                return False
            
        return True
        
        
    def is_valid_password(password: str) -> bool:
        # least 6 chars, max 15 lets say it can be anything special symbols chars or digits, 
        return len(password) >= 6 and len(password) <= 15
    
    
    def is_valid_email(email: str) -> bool:
        try:
            # Validate.
            valid = validate_email(email)
            # Update with the normalized form.
            email = valid.email
            return True
        except EmailNotValidError:
            return False
        

    def is_valid_phone_number(phone_number: str) -> bool:
        # lets say phone num must be 9 chars in len, no less, no more
        phone_number = phone_number.strip()
        length = len(phone_number)
        
        if " " in phone_number:
            return False
        
        if length != 9:
            return False
        
        for digit in phone_number:
            if digit.isalpha():
                return False
            
        return True


    def is_valid_personal_id(personal_id: str) -> bool:
        # lets say personal ID must be 11 chars in len
        personal_id = personal_id.strip()
        length = len(personal_id)
        
        if " " in personal_id:
            return False
        
        if length != 11:
            return False
        
        for digit in personal_id:
            if digit.isalpha():
                return False
            
        return True
        

    def is_valid_account_number(account_number: str) -> bool:
        users = JsonFileTasks(User('','','','','','',).file_path).load_data()
        for user in users.values():
            if account_number == user["account_number"]:
                return True
        return False


class Functionalities():
    
    def generate_account_number() -> str:
        # num sample GB0000AB0000A00 max len = 15
        
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        account_number = ""
        bank_code = "GB"
        country_code = "GE"
        
        first_two_digits = random.randint(0, 99)
        first_two_digits = "0" * (2 - len(str(first_two_digits))) + str(first_two_digits)
        
        first_four_digits = random.randint(0, 9999)
        first_four_digits = "0" * (4 - len(str(first_four_digits))) + str(first_four_digits)
         
        first_two_chars = chars[random.randint(0, 25)] + chars[random.randint(0, 25)]
        
        second_four_digits = random.randint(0, 9999)
        second_four_digits = "0" * (4 - len(str(second_four_digits))) + str(second_four_digits) 
        
        one_char = chars[random.randint(0, 25)]
        
        last_two_digits = random.randint(0, 99)
        last_two_digits = "0" * (2 - len(str(last_two_digits))) + str(last_two_digits)
        
        account_number = country_code + first_two_digits + bank_code + first_four_digits + first_two_chars + second_four_digits + one_char + last_two_digits
        
        return account_number
  
  
    def generate_pin_code() -> str:
        return str(random.randint(1000, 9999))
      
      
    def current_date() -> datetime:
        return date.today()
    
    
    def current_time() -> str:
        current = datetime.now()

        hour = current.hour
        minute = current.minute
        sec = current.second

        return f"{hour}:{minute}:{sec}"
    

    def add_months(date, months) -> datetime:
        date = datetime.strptime(str(date), "%Y-%m-%d").date()
        new_month = date.month + months
        new_year = date.year + new_month // 12
        new_month = new_month % 12

        if new_month == 0:
            new_month = 12
            new_year -= 1

        last_day_of_new_month = (datetime(new_year, new_month, 1) - timedelta(days=1)).day
        new_day = min(date.day, last_day_of_new_month)

        return datetime(new_year, new_month, new_day).date()
  
    
    def compare_dates(date1, date2):    
    
        date1 = date1.split("-")
        date2 = date2.split("-")
        
        for i in range(0, 3):
            if int(date1[i]) > int(date2[i]):
                return 1
            elif int(date1[i]) < int(date2[i]):
                return -1
        return 0
     
class JsonFileTasks():
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        
    def load_data(self) -> dict:
        try:
            with open(self.file_path, "r") as accounts_data:
                data = json.load(accounts_data)
                return data if len(data) >= 1 else {}
        except Exception:
            return {}
        
    
    def save_data(self, data: dict):
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)
            