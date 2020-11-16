# Simple Banking

A python based terminal application integrated with sqllite3 In this application the focus is on Luhn algorithm and how to integrate with sqllite3 package to do CRUD operations on all the feaures that are available.

### Architecture
The App is divided into:
- Two main menus `Authentication menu` and `Bank Account Menu`
- Where Menus can only interact with the `Bank` and `Auth` Controller
- Only The Controller will have access to the "Database" (An abstraction layer from the SQL code)

### Features:
1. Register account 
2. Login
3. All cards issued are validated based on [Luhn algorithm](https://en.wikipedia.org/wiki/Luhn_algorithm)
4. View Balance
5. Add Balance
6. Transfer Money to other account
7. Close account

### How it works
`python banking/bank.py`

```bash
1. Create an account
2. Log into account
0. Exit
>1

Your card have been created
Your card number:
4000009455296122
Your card PIN:
1961

1. Create an account
2. Log into account
0. Exit
>1

Your card have been created
Your card number:
4000003305160034
Your card PIN:
5639

1. Create an account
2. Log into account
0. Exit
>2

Enter your card number:
>4000009455296122
Enter your PIN:
>1961

You have successfully logged in!

1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
>2

Enter income:
>10000
Income was added!

1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
>1

Balance: 10000

1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
>3

Transfer
Enter card number:
>4000003305160035
Probably you made a mistake in the card number. Please try again!

1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
>3

Transfer
Enter card number:
>4000003305061034
Such a card does not exist.

1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
>3

Transfer
Enter card number:
>4000003305160034
Enter how much money you want to transfer:
>15000
Not enough money!

1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
>3

Transfer
Enter card number:
>4000003305160034
Enter how much money you want to transfer:
>5000
Success!

1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
>1

Balance: 5000

1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit

>0
Bye!
```

### Requirements
Tested to work and run properly on python 3.8.5
