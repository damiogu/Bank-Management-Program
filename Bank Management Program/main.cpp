#include <iostream>
#include <fstream>
#include <vector>
#include <iomanip>
using namespace std;

class Account {
public:
    string accountNumber;
    string name;
    double balance;

    Account() {}
    Account(string accNo, string accName, double accBalance) {
        accountNumber = accNo;
        name = accName;
        balance = accBalance;
    }
};

class Bank {
private:
    vector<Account> accounts;

    void saveToFile() {
        ofstream file("accounts.dat", ios::trunc);
        for (auto &acc : accounts) {
            file << acc.accountNumber << " " << acc.name << " " << acc.balance << endl;
        }
        file.close();
    }

    void loadFromFile() {
        accounts.clear();
        ifstream file("accounts.dat");
        if (file.is_open()) {
            string accNo, name;
            double balance;
            while (file >> accNo >> name >> balance) {
                accounts.push_back(Account(accNo, name, balance));
            }
            file.close();
        }
    }

public:
    Bank() {
        loadFromFile();
    }

    void createAccount() {
        string accNo, name;
        double balance;
        cout << "Enter Account Number: "; cin >> accNo;
        cout << "Enter Name: "; cin >> name;
        cout << "Enter Initial Deposit: "; cin >> balance;
        accounts.push_back(Account(accNo, name, balance));
        saveToFile();
        cout << "Account created successfully!" << endl;
    }

    void deposit() {
        string accNo;
        double amount;
        cout << "Enter Account Number: "; cin >> accNo;
        cout << "Enter Amount to Deposit: "; cin >> amount;
        for (auto &acc : accounts) {
            if (acc.accountNumber == accNo) {
                acc.balance += amount;
                saveToFile();
                cout << "Deposit successful! New Balance: " << acc.balance << endl;
                return;
            }
        }
        cout << "Account not found!" << endl;
    }

    void withdraw() {
        string accNo;
        double amount;
        cout << "Enter Account Number: "; cin >> accNo;
        cout << "Enter Amount to Withdraw: "; cin >> amount;
        for (auto &acc : accounts) {
            if (acc.accountNumber == accNo) {
                if (acc.balance >= amount) {
                    acc.balance -= amount;
                    saveToFile();
                    cout << "Withdrawal successful! New Balance: " << acc.balance << endl;
                } else {
                    cout << "Insufficient funds!" << endl;
                }
                return;
            }
        }
        cout << "Account not found!" << endl;
    }

    void checkBalance() {
        string accNo;
        cout << "Enter Account Number: "; cin >> accNo;
        for (auto &acc : accounts) {
            if (acc.accountNumber == accNo) {
                cout << "Account Holder: " << acc.name << " | Balance: " << fixed << setprecision(2) << acc.balance << endl;
                return;
            }
        }
        cout << "Account not found!" << endl;
    }
};

int main() {
    Bank bank;
    int choice;
    while (true) {
        cout << "\nBANK MANAGEMENT SYSTEM" << endl;
        cout << "1. Create Account" << endl;
        cout << "2. Deposit Money" << endl;
        cout << "3. Withdraw Money" << endl;
        cout << "4. Check Balance" << endl;
        cout << "5. Exit" << endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1: bank.createAccount(); break;
            case 2: bank.deposit(); break;
            case 3: bank.withdraw(); break;
            case 4: bank.checkBalance(); break;
            case 5: exit(0);
            default: cout << "Invalid choice!" << endl;
        }
    }
}