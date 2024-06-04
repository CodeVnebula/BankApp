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

class Email():
    def __init__(self, email_account_to: str) -> None:
        self.bank_email, self.password = self.get_bank_email()
        self.email_account_to = email_account_to
        
    
    def send_email(self, subject: str, email_body: str) -> Tuple[bool, str]:
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
                "withdrawal_disabled_date" : ""
            } 

        JsonFileTasks(self.file_path).save_data(data)
        return self.pin_code, self.account_number
     
       
    def login_verification(self, email: str, password: str) -> bool:
        users = JsonFileTasks(self.file_path).load_data()
        for user in users.values():
            if user['email'] == email and user['password'] == self.hash_password(password):
                return True
        return False
    
   
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
    
    
    def change_pin_code(self, new_pin_code: str) -> Tuple[bool, str]:
        if len(new_pin_code) != 4:
            error_message = "PIN code must be 4 digits in length"
            return False, error_message

        for digit in new_pin_code:
            if digit.isalpha():
                error_message = "PIN code must contain only digits"
                return False, error_message
        
        data = JsonFileTasks(self.file_path).load_data()
        
        if data[personal_id]["pin_code_changed_manually"] == True:
            error_message = "You can change PIN code only once!"
            return False, error_message
        
        if Validation.is_valid_email(self.email):
            for personal_id, details in data.items():
                if details["email"] == self.email:
                    personal_id = personal_id
                    break
        
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
            error_message = "Please enter valid amount, Error Msg:" + ve
            return False, error_message
            
        personal_id = self.get_personal_id_by_account_number(self.account_number)
        if not personal_id:
            error_message = "Personal ID Error"
            return False, error_message
        
        if amount <= 0:
            return False, "Insufficient funds"
        
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
        
        return True, filling_message
        
        
    def withdraw(self, amount: str | float | int, inputted_pin_code: str) -> Tuple[bool, str]:
        try:
            amount = abs(float(amount))
        except ValueError as ve:
            error_message = "Please enter valid amount, Error Msg:" + ve
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
        
        return True, withdrawal_message
    
    
    def transfer(self, amount: str | float | int, account_number_to: str) -> Tuple[bool, str] | Tuple[str, str]:
        try:
            amount = abs(float(amount))
        except ValueError as ve:
            error_message = "Please enter valid amount, Error Msg:" + ve
            return False, error_message
        
        if account_number_to == self.account_number:
            error_message = "It seems like account number you entered is your account. Please double-check and try again."
            return False, error_message
            
        personal_id_acc_from = self.get_personal_id_by_account_number(self.account_number)
        personal_id_acc_to = self.get_personal_id_by_account_number(account_number_to)
        
        print(personal_id_acc_from)
        print(personal_id_acc_to)
        
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
        
        return transfer_message_acc_from, transfer_message_acc_to
    
    
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
        
        loan_message = f"Balance was filled By GB Bank, Account: {self.account_number}. Amount - {self.amount}, {current_date}. (loan)"
        history[self.account_number]["balance_filling_history"].append(loan_message)
        
        loan_data[self.account_number] = {
            "loan_approved_date" : str(current_date) + " 00:00:00",
            "loan_expires_date" : str(last_date),
            "time_period" : self.time_period,
            "amount_borrowed" : self.amount,
            "total_repayment" : total_repayment,
            "interest_rate" : interest_rate,
            "min_monthly_payment" : min_monthly_payment,
            "loan_status" : True
        }
        
        JsonFileTasks(self.data_file_path).save_data(account_dets)
        JsonFileTasks(self.history_file_path).save_data(history)
        JsonFileTasks(self.loan_data_file_path).save_data(loan_data)
        
        return True, "Loan Successfully approved"
    
    
    def pay_monthly_loan(self):
        pass
    
    
    def check_loan_details(self) -> dict:
        loan_details = JsonFileTasks(self.loan_data_file_path).load_data()
        return loan_details[self.account_number]
        

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
        new_month = date.month + months
        new_year = date.year + new_month // 12
        new_month = new_month % 12

        if new_month == 0:
            new_month = 12
            new_year -= 1

        last_day_of_new_month = (datetime(new_year, new_month + 1, 1) - timedelta(days=1)).day
        new_day = min(date.day, last_day_of_new_month)

        return datetime(new_year, new_month, new_day)
  
     
class JsonFileTasks():
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        
    def load_data(self) -> dict:
        try:
            with open(self.file_path, "r") as accounts_data:
                data = json.load(accounts_data)
                return data
        except FileNotFoundError:
            return {}
        
    
    def save_data(self, data: dict):
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)
