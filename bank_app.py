import json
import json
import random
import hashlib
from datetime import date
from email_validator import validate_email, EmailNotValidError

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
            return "Oops! It seems like the first name you entered doesn't meet our requirements. Please try a different username."
        
        if not Validation.is_valid_name_surname(self.last_name):
            return "Oops! It seems like the last name you entered doesn't meet our requirements. Please try a different username."
        
        if not Validation.is_valid_email(self.email):
            return "Oops! It seems the email you entered is invalid. Please double-check and try again."
        
        if not Validation.is_valid_personal_id(self.personal_id):
            return "Oops! It seems the personal ID you entered is invalid. Please double-check and try again."
        
        if not Validation.is_valid_phone_number(self.phone_number):
            return "Oops! It seems like phone number you entered is invalid or doesn't meet our requirements. Please double-check and try again."
        
        if not Validation.is_valid_password(self.password):
            return "Oops! It seems like password you entered doesn't meet our requirements. Please double-check and try again."
        
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
                "balance" : 0.0
            }
            
        else:
            if self.personal_id in data:
                return "Oops! It seems the personal ID you entered or already registered. Please double-check and try again."
            
            for info in data.values():
                if info["email"] == self.email:
                    return "Opps! It seems the email you entered is already registered. Please double-check and try again."
            
                if info["phone_number"] == self.phone_number:
                    return "Opps! It seems the phone number you entered is already registered. Please double-check and try again."
            
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
                "balance" : 0.0
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
            print(str(e))
            # Email is not valid, exception message is human-readable
            print(str(e))
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
        return str(random.randint(0, 9999))
      
      
    def current_date():
        return date.today()
     
     
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
    
    def update_data(self):
        pass
    
user = User("giorgi", "chkhikvadze", "12345678910", "123456789", "cpmgeoo@gmail.com", "1234567")
# user.create_bank_account()
# print(user.login_veirfication( "cpmgeoo@gmail.com", "1234567"))