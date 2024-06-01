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

class Email():
    def __init__(self, email_account_to) -> None:
        self.bank_email, self.password = self.get_bank_email()
        self.email_account_to = email_account_to
        
    
    def send_email(self, subject, email_body):
        if not Validation.is_valid_email(self.email_account_to):
            print("Oops! It seems the email you entered is invalid. Please double-check and try again.")
            return False
        
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
                return True
        except smtplib.SMTPAuthenticationError as e:
            print("Failed to authenticate with the SMTP server:", e)
            return False
        except smtplib.SMTPRecipientsRefused as e:
            print("All recipient addresses were refused:", e)
            return False
        except smtplib.SMTPSenderRefused as e:
            print("The sender address was refused:", e)
            return False
        except smtplib.SMTPDataError as e:
            print("The SMTP server replied with an unexpected error code:", e)
            return False
        except smtplib.SMTPConnectError as e:
            print("Failed to connect to the SMTP server:", e)
            return False
        except smtplib.SMTPHeloError as e:
            print("The server refused our HELO message:", e)
            return False
        except smtplib.SMTPNotSupportedError as e:
            print("The SMTP server does not support the STARTTLS extension:", e)
            return False
        except smtplib.SMTPException as e:
            print("An error occurred during the SMTP transaction:", e)
            return False
        except Exception as e:
            print("An unexpected error occurred:", e)
            return False

    @staticmethod
    def get_bank_email():
        try:
            with open("bank_email_and_passcode.txt", "r") as bank_email:
                email, password = bank_email.readlines()
                return email, password
        except FileNotFoundError as e:
            print("Couldn't find the bank email information", e)
            return None, None   
    
    
    @staticmethod
    def verification_code():
        return str(random.randint(100000, 999999))
    
    
    
class User():
    def __init__(self, first_name, last_name, personal_id, phone_number, email, password) -> None:
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
    
    def create_bank_account(self):
        if not Validation.is_valid_name_surname(self.first_name):
            print("Oops! It seems like the first name you entered doesn't meet our requirements. Please try a valid first name.")
            return False

        if not Validation.is_valid_name_surname(self.last_name):
            print("Oops! It seems like the last name you entered doesn't meet our requirements. Please try a valid last name.")
            return False
        
        if not Validation.is_valid_email(self.email):
            print("Oops! It seems the email you entered is invalid. Please double-check and try again.")
            return False
        
        if not Validation.is_valid_personal_id(self.personal_id):
            print("Oops! It seems the personal ID you entered is invalid. Please double-check and try again.")
            return False
        
        if not Validation.is_valid_phone_number(self.phone_number):
            print("Oops! It seems like phone number you entered is invalid or doesn't meet our requirements. Please double-check and try again.")
            return False
        
        if not Validation.is_valid_password(self.password):
            print("Oops! It seems like password you entered doesn't meet our requirements. Please double-check and try again.")
            return False

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
                "withdrawal_disabled_date" : ""
            }
            
        else:
            if self.personal_id in data:
                print("Oops! It seems the personal ID you entered or already registered. Please double-check and try again.")
                return False
            
            for info in data.values():
                if info["email"] == self.email:
                    print("Opps! It seems the email you entered is already registered. Please double-check and try again.")
                    return False
            
                if info["phone_number"] == self.phone_number:
                    print("Opps! It seems the phone number you entered is already registered. Please double-check and try again.")
                    return False
            
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
     
       
    def login_veirfication(self, email, password):
        users = JsonFileTasks(self.file_path).load_data()
        for user in users.values():
            if user['email'] == email and user['password'] == self.hash_password(password):
                return True
        return False
    
   
    def hash_password(self, password):
        # sha256 function for hashing input, func returns str
        return hashlib.sha256(password.encode()).hexdigest()
 

    def get_user_details(self, email):
        data = JsonFileTasks(self.file_path).load_data()

        for personal_id, details in data.items():
            if details["email"] == email:
                personal_info = data[personal_id]
    
        return personal_info
    
    
    def change_password(self, new_password):
        if not Validation.is_valid_password(new_password):
            print("Oops! It seems like password you entered doesn't meet our requirements. Please double-check and try again.")
            return False
        data = JsonFileTasks(self.file_path).load_data()
        if Validation.is_valid_email(self.email):
            for personal_id, details in data.items():
                    if details["email"] == self.email:
                        personal_id = personal_id
                        break
            data[personal_id]["password"] = self.hash_password(new_password)
            JsonFileTasks(self.file_path).save_data(data)
            return True
        return False
    
    
    def change_pin_code(self, new_pin_code):
        if len(new_pin_code) != 4:
            print("PIN code must be 4 digits in length")
            return False

        for digit in new_pin_code:
            if digit.is_alpha():
                print("PIN code must contain only digits")
                return False
        
        data = JsonFileTasks(self.file_path).load_data()
        if Validation.is_valid_email(self.email):
            for personal_id, details in data.items():
                if details["email"] == self.email:
                    personal_id = personal_id
                    break
        
            data[personal_id]['pin_code'] = new_pin_code
            JsonFileTasks(self.file_path).save_data(data)
            return True
        return False
        
        




class Account():
    def __init__(self, account_number) -> None:
        self.account_number = account_number
        self.account_history_file_path = "Data/accounts_history.json"
        self.data_file_path = "Data/accountsData.json"
        self.data = JsonFileTasks(self.data_file_path).load_data()
        self.number_of_tries = 0
        
    def get_personal_id_by_account_number(self, acc_number):
        if Validation.is_valid_account_number(acc_number):
            for personal_id, details in self.data.items():
                if details["account_number"] == acc_number:
                    return personal_id
            return None

    def deposit(self, amount):
        personal_id = self.get_personal_id_by_account_number(self.account_number)
        if personal_id == False:
            print("PIE")
            return False
        
        if amount <= 0:
            print("Insufficient funds")
            return False
        
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
        
        return filling_message
        
        
    def withdraw(self, amount, inputted_pin_code):
        print(self.number_of_tries)
        
        personal_id = self.get_personal_id_by_account_number(self.account_number)
        if not personal_id:
            print("pID-Err")
            return False
        
        if self.data[personal_id]["withdrawal_disabled_date"] == str(Functionalities.current_date()):
            print("It seems you have entered wrong pin code few times, you won't be able to make withdrawal for one day!")
            return False
        else:
            self.data[personal_id]["withdrawal_disabled_date"] = ""
            JsonFileTasks(self.data_file_path).save_data(self.data)
        
        pin_code = self.data[personal_id]["pin_code"]
        
        if pin_code != inputted_pin_code:
            if self.number_of_tries == 3:
                self.data[personal_id]["withdrawal_disabled_date"] = str(Functionalities.current_date())
                JsonFileTasks(self.data_file_path).save_data(self.data)
                print("It seems you have entered wrong pin code few times, you won't be able to make withdrawal for one day!")
                return False
            
            self.number_of_tries += 1
            print("It seems pin code you have entered does not match your pin code. Please double-check and try again.")
            return False
        
        balance = self.data[personal_id]["balance"]
        
        if amount > balance:
            print("Insufficient funds")
            return False
        
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
        
        return withdrawal_message
    
    
    def transfer(self, amount, account_number_to):
        if account_number_to == self.account_number:
            print("It seems like account number you entered is your account. Please double-check and try again.")
            return False
            
        personal_id_acc_from = self.get_personal_id_by_account_number(self.account_number)
        personal_id_acc_to = self.get_personal_id_by_account_number(account_number_to)
        
        print(personal_id_acc_from)
        print(personal_id_acc_to)
        
        if not personal_id_acc_from:
            print("Error")
            return False
        
        if not personal_id_acc_to:
            print("Error, finding account number to")
            return False
        
        balance_account_number_from = self.data[personal_id_acc_from]["balance"]
        balance_account_number_to = self.data[personal_id_acc_to]["balance"]
        
        if amount > balance_account_number_from:
            print("Insufficient funds")
            return False
        
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
    
    
    def get_transaction_history(self):
        account_history = JsonFileTasks(self.account_history_file_path).load_data()
        return account_history[self.account_number]["transaction_history"]
    
    
    def get_balance_filling_history(self):
        account_history = JsonFileTasks(self.account_history_file_path).load_data()
        return account_history[self.account_number]["balance_filling_history"]
    
    
    def get_withdrawal_history(self):
        account_history = JsonFileTasks(self.account_history_file_path).load_data()
        return account_history[self.account_number]["withdrawal_history"]
      
      
class Loan():
    def __init__(self, amount, account_number, time_period) -> None:
        self.annual_interest_rate = 0.08    # 8%
        self.amount = amount
        self.account_number = account_number
        self.time_period = time_period
        self.loan_data_file_path = "Data/loan_data.json"
        self.data_file_path = "Data/accountsData.json"
        self.history_file_path = "Data/accounts_history.json"
        
    
    def interest_rate(self):
        if (self.amount <= 0 or self.amount > 100000) or (self.time_period < 6 or self.time_period > 48):
            return False
        
        return self.amount * self.annual_interest_rate * (self.time_period / 12)
    
    
    def set_up_loan_details(self):
        loan_data = JsonFileTasks(self.loan_data_file_path).load_data()
        
        if self.account_number in loan_data and loan_data["loan_status"] == True:
            print("It seems you have already got an active loan. Please finish it to be able to take a new loan.")
            return False
        
        interest_rate = self.interest_rate()
        
        if interest_rate == False:
            print("It seems details you have entered are wrong! Plase double-check ad try again.")
            return False
        
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
        
        return loan_data
        

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
        
        
    def is_valid_password(password):
        # least 6 chars, max 15 lets say it can be anything special symbols chars or digits, 
        return len(password) >= 6 and len(password) <= 15
    
    
    def is_valid_email(email):
        try:
            # Validate.
            valid = validate_email(email)
            # Update with the normalized form.
            email = valid.email
            return True
        except EmailNotValidError as e:
            return False
        

    def is_valid_phone_number(phone_number):
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


    def is_valid_personal_id(personal_id):
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
        

    def is_valid_account_number(account_number):
        users = JsonFileTasks(User('','','','','','',).file_path).load_data()
        for user in users.values():
            if account_number == user["account_number"]:
                return True
        return False


class Functionalities():
    
    def generate_account_number():
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
  
  
    def generate_pin_code():
        return str(random.randint(1000, 9999))
      
      
    def current_date():
        return date.today()
    
    
    def current_time():
        current = datetime.now()

        hour = current.hour
        minute = current.minute
        sec = current.second

        return f"{hour}:{minute}:{sec}"
    

    def add_months(date, months):
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
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        
    def load_data(self):
        try:
            with open(self.file_path, "r") as accounts_data:
                data = json.load(accounts_data)
                return data
        except FileNotFoundError:
            return {}
        
    
    def save_data(self, data):
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)
