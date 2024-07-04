from bank_app import User, Account, Loan, Email
from os import system
import textwrap
from time import sleep


def get_details(data):
    print("_____________ Account Details _____________\n")
    print(f"Account: {data['account_number']} \nPIN-code - {data['pin_code']}\n")
    print("User details: ")
    print(f"    - {data['first_name']} {data['last_name']}")
    print("Contact:")
    print(f"  Email - {data['email']}")
    print(f"  Phone - {data['phone_number']}")
    print(f"Account has been created since: {data['account_creation_date']}")


def display_history(history_data, hist_of=""):
    if not history_data:
        print(f"   - {hist_of} history is empty!")
    else:
        for hist_element in history_data:
            print(f"   - {hist_element}")
    print()


def display_loan_details(loan, loan_details):
    if loan_details == None:
        print("No loan details for this account")
        return
    print("_____________ Loan Details _____________\n")
    print(f"   - Loan approved date: {loan_details["loan_approved_date"]}")
    print(f"   - Loan expires date: {loan_details["loan_expires_date"]}")
    print(f"   - Loan time period (months): {loan_details["time_period"]}")
    print(f"   - Amount borrowed: {loan_details["amount_borrowed"]}")
    print(f"   - Total repayment: {loan_details["total_repayment"]}")
    print(f"   - Interest rate: {loan_details["interest_rate"]}")
    print(f"   - Minimum monthly payment: {loan_details["min_monthly_payment"]}")
    print(f"   - Returned amount: {loan_details["amount_returned"]}")
    print(f"   - Amount left to pay: {loan_details["amount_left"]}")
    print(f"   - Next payment date: {loan_details["next_payment_date"]}")
    print(f"   - Loan active status: {"active" if loan_details["loan_status"] else "not active"}")
    
    print("\nSee when you paid? (y/n) ")
    choice = input(">> ")
    if choice == 'y':
        display_loan_payment_dates(loan.get_loan_payment_dates())
    else:
        print("Quiting...")

def handle_registration():
    print("\n___________ Registration ___________\n")
    first_name = input("First name: ").capitalize()
    last_name = input("Last name: ").capitalize()
    personal_id = input("Personal ID: ")
    phone_number = input("Phone number: ")
    email = input("Email: ")
    password = input("Password: ")

    em = Email(email_account_to=email)
    verification_code = em.verification_code()
    body = f"{verification_code} is your GB bank verification code."

    print(f"\nTo make sure {email} belongs to you, we will send 6 digit verification code to the email...")
    result, message = em.send_email("Verification code", body)

    if result:
        user_input = input(f"Enter the 6 digit code we sent to {email}: ")
        if user_input != str(verification_code):
            print("Unsuccessful verification. Make sure you have entered the code correctly!")
            return
        
        user = User(first_name=first_name, last_name=last_name, personal_id=personal_id,
                    phone_number=phone_number, email=email, password=password)
        result, message = user.create_bank_account()
        if not result:
            print(message)
        else:
            pin_code, account_number = result, message
            print(f"Congratulations {first_name}, your bank account has been successfully created!")
            
            subject = "Account created"
            account_created_message = textwrap.dedent(f"""
                - Hello {first_name}, your bank account has been successfully created!
                Account details:
                - Account number: {account_number}.
                - PIN code: {pin_code}.
                You can change your PIN code anytime but only once. We strongly suggest
                to change PIN code.
                Please keep this information secure and do not share your PIN code with 
                anyone.
                Thank you for choosing our bank. We are excited to have you with us and 
                look forward to serving you!
                Best regards,
                Your Bank Team
            """)

            result,message = em.send_email(subject, account_created_message)
            if not result:
                print(message)
    else:
        print(message)


def handle_login():
    print("\n___________ Login ___________\n")
    wrong_password_input_count = 0

    while wrong_password_input_count < 3:
        email = input("Email: ")
        password = input("Password: ")

        user = User('', '', '', '', email, password)
        result, message = user.login_verification(email, password)
        if result:
            print(message)
            handle_account_menu(user)
            return
        else:
            if message == "Invalid password. Please try again.":
                wrong_password_input_count += 1
                print(message)
            else:
                print(message)
                return 
            
    print("It seems like you forgot your password.")
    forgot_password = input("Do you want to reset it? (y/n): ").lower()
    if forgot_password == 'y':
        reset_password()
    elif forgot_password == 'n':
        print("Quitting!")
    else:
        print("Invalid Choice! ")


def reset_password():
    email_account = input("Enter email: ")
    email = Email(email_account)
    verification_code = email.verification_code()
    subject = "Verification code"
    body = f"Your password reset verification code is {verification_code}"
    result, message = email.send_email(subject=subject, email_body=body)

    if result:
        user_input = input("Enter the 6 digit verification code: ")
        if user_input == verification_code:
            new_password = input("Enter new password: ")
            user = User("", "", "", "", email_account, new_password)
            print(user.change_password(new_password)[1])
        else:
            print("Incorrect verification code. Try again later!")
    else:
        print(message)


def handle_account_menu(user):
    account_number = user.get_user_details(user.email)["account_number"]
    account = Account(account_number)
    
    while True:
        print("\n____ Account Menu ____")
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

        if choice == "1":
            amount = input("Amount to deposit: ")
            print(account.deposit(amount)[1])
        elif choice == "2":
            amount = input("Amount to withdraw: ")
            pin_code = input("Pin code: ")
            print(account.withdraw(amount=amount, inputted_pin_code=pin_code)[1])
        elif choice == "3":
            account_number_to = input("Account number to transfer: ")
            amount = input("Amount to transfer: ")
            print(account.transfer(amount=amount, account_number_to=account_number_to)[1])
        elif choice == "4":
            balance = user.get_user_details(user.email)["balance"]
            print(f"____________ Balance ____________\nAccount: {account_number}\nAvailable balance: {balance}$")
        elif choice == "5":
            get_details(user.get_user_details(user.email))
        elif choice == "6":
            handle_account_history(account)
        elif choice == "7":
            handle_loan_options(account)
        elif choice == "8":
            manage_account(user, account_number)
        elif choice == "9":
            print("Logging out!")
            sleep(2)
            system("cls")
            break
        else:
            print("Invalid choice. Please try again.")


def handle_account_history(account):
    print("___________ Account History ___________\n")
    print("1. View Balance filling history")
    print("2. View Transaction history")
    print("3. View Withdrawal history")
    print("4. Quit")

    hist_choice = input(">> ")

    if hist_choice == '1':
        display_history(account.get_balance_filling_history(), "Balance filling")
    elif hist_choice == '2':
        display_history(account.get_transaction_history(), "Transaction")
    elif hist_choice == '3':
        display_history(account.get_withdrawal_history(), "Withdrawal")
    elif hist_choice == "4":
        return
    else:
        print("Invalid choice. Please try again.")


def handle_loan_options(account):
    print("_______________ Loan Options_______________\n")
    print("1. Apply for loan")
    print("2. Pay monthly loan")
    print("3. Check loan details")

    choice = input(">> ")
    if choice == "1":
        amount = input("Loan amount max(100'000$ at once): ")
        time_period = input("Time period 'months', min-6 months, max-48: ")
        loan = Loan(amount=amount, account_number=account.account_number, time_period=time_period)
        print(loan.set_up_loan_details()[1])
            
    elif choice == "2":
        amount = input("Amount to return: ")
        loan = Loan(amount=amount, account_number=account.account_number, time_period="")
        print(loan.pay_monthly_loan()[1])
        
    elif choice == "3":
        loan = Loan(0, account.account_number, "")
        display_loan_details(loan, loan.check_loan_details())
        
    else:
        print("Invalid choice. Please try again.")

def display_loan_payment_dates(payment_data: list):
    if payment_data is None or len(payment_data) == 0:
        print("No payment data yet.")
        return
    print("______ Dates When You Paid ______")
    print(" _______________________")
    print("|    Date    |  Amount  |")
    print(" -----------------------")
    
    for entry in payment_data:
        for date, amount in entry.items():
            print(f"| {date} | {amount}{(9 - len(amount)) * ' '}|")
    
    print(" -----------------------")

def manage_account(user, account_number):
    print("_____ Account Management _____\n")
    print("1. Change password")
    print("2. Change PIN code")
    print("3. Deactivate Account")

    user_choice = input(">> ")
    
    if user_choice == "1":
        reset_password()
    elif user_choice == "2":
        new_pin = input("Enter new PIN code: ")
        _, message = user.change_pin_code(new_pin, account_number)
        print(message)
    elif user_choice == "3":
        print("Are you sure you want to deactivate your account? (y/n)")
        choice = input(">> ").lower()
        
        if choice == "y":
            email = input("Enter your email: ")
            verification_code = Email(email).verification_code()
            subject = "Account deactivation"
            body = f"your account deactivation verification code is {verification_code}"
            result, message = Email(email).send_email(subject, body)
            if result:
                user_input = input("Enter the 6 digit verification code: ")
                if user_input == verification_code:
                    print(user.deactivate_account()[1])
                    main()
                else:
                    print("Incorrect verification code. Try again later!")
            else:
                print(message)
        elif choice == "n":
            print("Quitting!")
    else:
        print("Invalid choice. Please try again.")


def main():
    print("\n_________________ Bank App _________________\n")
    
    while True:
        print("1. Create a bank account")
        print("2. Login")
        print("3. Exit")

        your_choice = input(">> ")

        if your_choice == "1":
            handle_registration()
        elif your_choice == "2":
            handle_login()
        elif your_choice == "3":
            print("Leaving Bank App. Thank you for visiting us ^_^. Goodbye!\n")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
