from bank_app import User, Account, Loan, Email
from os import system
import textwrap
from time import sleep


def get_details(data):
    print("_____________ Account Details _____________\n")
    print(f"Account: {data["account_number"]} \nPin-code - {data["pin_code"]}\n")
    
    print("User details: ")
    print(f"    - {data["first_name"]} {data["last_name"]}")
    print("Contact:")
    print(f"  Email - {data["email"]}")
    print(f"  Phone - {data["phone_number"]}")
    print(f"Account has been created since: {data["account_creation_date"]}")
    
    
def display_history(history_data, hist_of = ""):
    if not history_data:
        print(f"   - {hist_of} history is empty!")
    
    else:
        for hist_element in history_data:
            print(f"   - {hist_element}")
        
    print()
    
    
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
                
                em = Email(email_account_to=email)
                verification_code = em.verification_code()
                
                # print(verification_code)
                
                body = f"{verification_code} is your GB bank verification code."

                print(f"\nTo make sure {email} belongs to you, we will send 6 digit verification code to the email...")
                
                sent = em.send_email("Verification code", body)
                
                if sent == True:
                    print(f"Enter 6 digit code we sent to you on email: {email}.")
                    user_input = input(">> ")
                    
                    if str(user_input) != str(verification_code):
                        print("Unsuccessfull verification. Make sure you have entered code correctly!")
                        break
                else:
                    sleep(2)
                    system("cls")
                    break
                    
                print("Verified successfully!")

                user = User(first_name=first_name, last_name=last_name, personal_id=personal_id, 
                            phone_number=phone_number, email=email, password=password)
                
                result = user.create_bank_account()
                if result is not False:
                    pin_code, account_number = result
                    print(f"Congratulations {first_name} your bank account has been Successfully created!")
                    print(f"    - Account number: {account_number}\n    - Pin code: {pin_code}")
                    
                    subject = "Account created"
                    account_created_message = textwrap.dedent(f"""
                        - Hello {first_name} your bank account has been successfully created!
                        Account details:
                        - Account number: {account_number}.
                        - PIN code: {pin_code}.
                        Please keep this information secure and do not share your PIN code with 
                        anyone.
                        Thank you for choosing our bank. We are excited to have you with us and 
                        look forward to serving you!
                        Best regards,
                        Your Bank Team
                    """)
                    
                    sent_created_message = em.send_email(subject, account_created_message)
                    
                    if sent_created_message == True:
                        break
                    
                else:
                    break
                
        elif your_choice == "2":
            print("\n___________ Login ___________\n")
            wrong_password_input_count = 0
            while True:
                
                if wrong_password_input_count == 3:
                    print("\nIt seems like you forgot your password. If you're typing wrong email, please make sure")
                    print("you type it correctly, if you forgot password and want to reset it type 'y', if not type ")
                    print("'n' and to skip this or type 'q' and quit program")
                    
                    while True:
                        forgot_password = input(">> ").lower()
                        if forgot_password == 'y':
                            email_account = input("Enter email: ")
                            
                            email = Email(email_account)
                            
                            verification_code = email.verification_code()
                            subject = "Verification code"
                            body = f"Your password reset verification code is {verification_code}"
                            
                            sent = email.send_email(subject=subject, email_body=body)
                            
                            if sent:
                                print("Enter 6 digit verification code that we sent to you")
                                user_input = input(">> ")
                                
                                if user_input == verification_code:
                                    print("Enter new password: ")
                                    while True:
                                        new_password = input(">> ")
                                    
                                        user = User("", "", "", "", email_account, password)
                                    
                                        result = user.change_password(new_password)
                                    
                                        if result:
                                            print("Password successfully changed!")
                                            break
                                        else:
                                            print("Something went wrong!")
                                            break
                                    break
                                else:
                                    print("You entered wrong code, Try again later!")
                                    break
                            
                            break
                                
                            
                        elif forgot_password == 'n':
                            wrong_password_input_count = 0
                            break
                        elif forgot_password == 'q':
                            print("Quiting the system!")
                            return
                        else:
                            print("It seems like you entered wrong option. Please double-check and try again!")
                
                    break
                    
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
                    print("5. Account details")
                    print("6. Account history")
                    print("7. Loan options")
                    print("8. Manage account")
                    print("9. Logout")
                    
                    choice = input("\n>> ")
                    
                    account_number = user.get_user_details(email)["account_number"]
                    account = Account(account_number)
                    
                    if choice == "1":
                        while True:
                            amount = float(input("Amount to deposit: "))
                            
                            result = account.deposit(amount)
                            
                            if result != False:
                                print("Successfull deposit!")
                                break
                        break
                
                    elif choice == "2":
                        while True:
                            amount = float(input("Amount to withdraw: "))
                            pin_code = input("Pin code: ")
                            
                            result = account.withdraw(amount=amount, inputted_pin_code=pin_code)
                            
                            if result != False:
                                print("Successfull withdrawal!")
                                break
                        break
                    
                    elif choice == "3":
                        while True:
                            print("Transfering by account number: ")
                            
                            account_number_to = input("Account number to transfer: ")
                            amount = float(input("Amount to transfer: "))
                    
                            result = account.transfer(amount=amount, account_number_to=account_number_to)
                            
                            if result != False:
                                print("Successfull transaction!")
                                break
                        break
                            
                    elif choice == "4":
                        balance = user.get_user_details(email)["balance"]
                        print("____________ Balance ____________")
                        print(f"Account: {account_number}")
                        print(f"Avilable balance: {balance}$")
                        break
                    
                    elif choice == "5":
                        data = user.get_user_details(email)
                        get_details(data)
                        break
                    
                    elif choice == "6":
                        print("___________ Account History ___________\n")
                        
                        while True:
                            print("1. View Balance filling history")
                            print("2. View Transaction history")
                            print("3. View Withdrawal history")
                            print("4. Quit")
                            hist_choice = input(">> ")

                            if hist_choice == '1':
                                filling_history = account.get_balance_filling_history()
                                
                                print("______ Balance Filling History ______")
                                display_history(filling_history, "Balance filling")
                                break
                            
                            elif hist_choice == '2':
                                transaction_history = account.get_transaction_history()
                                
                                print("______ Transaction History ______")
                                display_history(transaction_history, "Transaction")
                                break
                            
                            elif hist_choice == '3':
                                withdrawal_history = account.get_withdrawal_history()
                                
                                print("______ Withdrawal History ______")
                                display_history(withdrawal_history, "Withdrawal")
                                break
                            
                            elif hist_choice == "4":
                                break
                                
                            else:
                                print("It seems like you have entered wrong option. Please double-check and try again.")
                            
                        
                    elif choice == "7":
                        print("_______________ Loan Options_______________\n")
                        print("1. Apply for loan")
                        print("2. Pay monthly loan")
                        print("3. Check loan details")
                        print

                        amount = float(input("Loan amount: "))
                        time_period = int(input("Time period 'months', min-6 months, max-48:"))
                        
                        loan = Loan(amount=amount, account_number=account_number, time_period=time_period)
                        
                        res = loan.set_up_loan_details()
                        print("succ")
                        print(res)
                        
                    elif choice == "8":
                        pass
                       
                    elif choice == "9":
                        break
                    
                    else:
                        pass
                    
                else:
                    print("Invalid email or password. Please try again.")
                    wrong_password_input_count += 1
                
        
        elif your_choice == "3":
            print("Leaving Bank App. Thank you for visiting us ^_^. Goodbye!\n")
            break
        
        else:
            print("It seems you entered wrong option. Please try again!")
        
        # system("cls")
        
if __name__ == "__main__":
    main()