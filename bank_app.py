import random
from datetime import date
from email_validator import validate_email, EmailNotValidError

class User():
    def __init__(self, first_name, last_name, personal_id, phone_number, email, password, initial_balance) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.personal_id = personal_id
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.initial_balance = initial_balance
        self.account_number = Functionalities.generate_account_number()
        self.pin_code = Functionalities.generate_pin_code()
        self.account_creation_date = Functionalities.current_date()
        self.file_path = "Data/accountsData.json"
    
    def create_bank_account(self):
        if not Validation.is_valid_name_surname(self.first_name):
            return ""
        
        if not Validation.is_valid_name_surname(self.last_name):
            return ""
        
        if not Validation.is_valid_email(self.email):
            return ""
        
        if not Validation.is_valid_personal_id(self.personal_id):
            return ""
        
        if not Validation.is_valid_phone_number(self.phone_number):
            return ""
        
        if not Validation.is_valid_password(self.password):
            return ""

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
            valid = validate_email(email)
            email = valid.email
            return True
        except EmailNotValidError as e:
            # print(str(e))
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
        
        first_four_digits = random.randint(0, 9999)
        first_four_digits = "0" * (4 - len(str(first_four_digits))) + str(first_four_digits)
         
        first_two_chars = chars[random.randint(0, 25)] + chars[random.randint(0, 25)]
        
        second_four_digits = random.randint(0, 9999)
        second_four_digits = "0" * (4 - len(str(second_four_digits))) + str(second_four_digits) 
        
        one_char = chars[random.randint(0, 25)]
        
        last_two_digits = random.randint(0, 99)
        last_two_digits = "0" * (2 - len(str(last_two_digits))) + str(last_two_digits)
        
        account_number = bank_code + first_four_digits + first_two_chars + second_four_digits + one_char + last_two_digits
        
        return account_number
  
  
    def generate_pin_code():
        return str(random.randint(0, 9999))
      
      
    def current_date():
        return date.today()
     
class JsonFileTasks():
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        
    def load_data(self):
        pass
    
    def save_data(self):
        pass
    
    def update_data(self):
        pass
    
user = User("giorgi", "chkhikvadze", "61808021325", "597008144", "cpmgeoo@gmail.com", "asdfg", 100)
print(Functionalities.generate_account_number())
print(Functionalities.generate_pin_code())
print(Functionalities.current_date())
print(Validation.is_valid_name_surname("asd43fs "))
print(Validation.is_valid_email("cpmgeoo@gmal.com"))
print(Validation.is_valid_phone_number("597008sd sd"))