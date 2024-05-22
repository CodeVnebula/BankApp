import random
from datetime import date

class User():
    def __init__(self, first_name, last_name, personal_id, phone_number, gmail, password, initial_balance) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.personal_id = personal_id
        self.phone_number = phone_number
        self.gmail = gmail
        self.password = password
        self.initial_balance = initial_balance
        self.account_number = Functionalities.generate_account_number()
        self.pin_code = Functionalities.generate_pin_code()
        self.account_creation_date = Functionalities.current_date()
    
    def create_bank_account(self):
        pass


class Validation():
    def is_valid_name(name):
        # lets say name cant be longer than 15 chars and less then 2 chars, cant contain spaces, 
        # cant have spaces around, cant contain digits
        
        name = name.strip()
        name_length = len(name)
        
        if name_length < 2 or name_length > 15:
            return "Name too long or too short!"
        
        if " " in name:
            return "Name can not contain spaces!"
        
        for char in name:
            if char.isdigit():
                return "Name can not contain digits!"
        
        
    def is_valid_password():
        # least 6 chars, max 15 lets say it can be anything special symbols chars or digits, 
        pass


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
    pass
    
user = User("giorgi", "chkhikvadze", "61808021325", "597008144", "cpmgeoo@gmail.com", "asdfg", 100)
print(Functionalities.generate_account_number())
print(Functionalities.generate_pin_code())
print(Functionalities.current_date())
print(Validation.is_valid_name("asd43fs "))