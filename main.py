from bank_app import User, Account
from os import system

def main():
    print("\n_________________ Bank App _________________\n")
    while True:
        print("1. Create a bank account")
        print("2. Login")
        print("3. Exit")
        
        your_choice = input(">> ")
        
        if your_choice == "1":
            print("\n___________ Registration ___________\n")
            
            while True:
                first_name = input("First name: ").capitalize()
                last_name = input("Last name: ").capitalize()
                personal_id = input("Personal ID: ")
                phone_number = input("Phone number: ")
                email = input("Email: ")
                password = input("Password: ")
                
                user = User(first_name=first_name, last_name=last_name, personal_id=personal_id, 
                            phone_number=phone_number, email=email, password=password)
                
                result = user.create_bank_account()
                if result is not False:
                    pin_code, account_number = result
                    print(f"Congratulations {first_name} your bank account has been Successfully created!")
                    print(f"    - Account number: {account_number}\n    - Pin code: {pin_code}")
                    break
        
        elif your_choice == "2":
            print("\n___________ Login ___________\n")
            
            while True:
                email = input("Email: ")
                password = input("Password: ")
            
                user = User('', '', '', '', email, password)
                if user.login_veirfication(email, password):
                    print("Successfull login")
                    print("\nAccount Menu")
                    print("1. Deposit")
                    print("2. Withdraw")
                    print("3. Transfer")
                    print("4. Check Balance")
                    print("5. Transaction History")
                    print("6. Apply for Loan")
                    print("7. Logout")
                    
                    choice = input("\n>> ")
                    
                    account_number = user.get_user_details(email)["account_number"]
                    account = Account(account_number)
                    
                    if choice == "1":
                        while True:
                            amount = float(input("Amount to deposit: "))
                            
                            result = account.deposit(amount)
                            
                            if result != False:
                                # print(result)
                                print("Successfull deposit!")
                                break
                        break
                
                    elif choice == "2":
                        while True:
                            amount = float(input("Amount to withdraw: "))
                            pin_code = input("Pin code: ")
                            
                            result = account.withdraw(amount=amount, inputted_pin_code=pin_code)
                            
                            if result != False:
                                # print(result)
                                print("Successfull withdrawal!")
                                break
                        break
                    
                    elif choice == "3":
                        pass
                    
                    elif choice == "4":
                        pass
                    
                    elif choice == "5":
                        pass
                    
                    elif choice == "6":
                        pass
                    
                    elif choice == "7":
                        pass
                    
                    else:
                        pass
                    
                else:
                    print("Invalid email or password. Please try again.")
                
        
        elif your_choice == "3":
            print("Leaving Bank App. Thank you for visiting us ^_^. Goodbye!\n")
            break
        
        else:
            print("It seems you entered wrong option. Please try again!")
        
        # system("cls")
        
if __name__ == "__main__":
    main()