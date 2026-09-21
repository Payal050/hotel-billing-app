# 🍽️ PetPuja – Hotel Billing Management System

PetPuja is a **Hotel Billing Management System** designed to simplify and digitize daily hotel/restaurant operations. The application helps manage menu items, tables, customers, reservations, billing, bill history, and reports through a user-friendly interface.

---

## 📌 Project Overview

Traditional hotel billing systems often involve manual calculations, paper-based records, and difficulty tracking previous transactions.

**PetPuja** provides a centralized digital system that allows hotel staff to:

* Manage menu items
* Manage tables
* Register and manage customers
* Handle reservations
* Create and generate bills
* Store billing history
* View sales and billing reports

The system is designed to reduce manual work, improve billing accuracy, and make hotel operations easier to manage.

---

## 🎯 Objectives

The main objectives of PetPuja are:

1. To automate the hotel billing process.
2. To reduce manual calculation errors.
3. To maintain customer and billing records digitally.
4. To manage restaurant tables efficiently.
5. To manage menu items and prices.
6. To maintain reservation information.
7. To provide access to previous bills and transaction history.
8. To generate useful reports for hotel management.

---

## 🚀 Features

### 🧾 POS Billing

* Create new customer orders
* Select menu items
* Specify item quantities
* Automatically calculate item totals
* Calculate the final bill amount
* Generate bills
* Save billing information

### 🍽️ Menu Management

* Add menu items
* View available menu items
* Manage item prices
* Organize food items

### 🪑 Table Management

* View hotel tables
* Manage table availability
* Assign tables to customers/orders

### 👥 Customer Management

* Add customer information
* Store customer details
* Access customer records

### 📅 Reservation Management

* Create reservations
* Store reservation details
* Manage customer booking information

### 📜 Bill History

* View previously generated bills
* Store transaction information
* Access historical billing records

### 📊 Reports

* View billing information
* Analyze transactions
* Generate useful business information

---

## 🏗️ Project Structure

```text
PetPuja/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
│
├── database/
│   └── hotel.db
│
├── templates/
│   ├── index.html
│   ├── billing.html
│   ├── menu.html
│   ├── customers.html
│   ├── tables.html
│   ├── reservations.html
│   ├── bill_history.html
│   └── reports.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── tests/
```

> File names may vary depending on the final version of the project.

---

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap

### Backend

* Python
* Flask

### Database

* SQLite

### Development Tools

* Visual Studio Code
* Git
* GitHub

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/PetPuja.git
```

### 2. Open the Project

```bash
cd PetPuja
```

### 3. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

Open the address in your browser.

---

## 📋 Main Modules

| Module          | Description                        |
| --------------- | ---------------------------------- |
| 🏠 Dashboard    | Overview of the hotel system       |
| 🧾 POS Billing  | Create and generate customer bills |
| 🍽️ Menu        | Manage food items and prices       |
| 🪑 Tables       | Manage hotel tables                |
| 👥 Customers    | Manage customer information        |
| 📅 Reservations | Manage table reservations          |
| 📜 Bill History | View previous transactions         |
| 📊 Reports      | View billing and sales information |

---

## 🔄 Billing Workflow

```text
Customer
   ↓
Select Table
   ↓
Select Menu Items
   ↓
Enter Quantity
   ↓
Calculate Total
   ↓
Generate Bill
   ↓
Save Bill
   ↓
Bill History
   ↓
Reports
```

---

## 🗄️ Database

PetPuja uses **SQLite** for storing application data.

The database can contain information related to:

* Customers
* Menu items
* Tables
* Reservations
* Bills
* Bill items
* Transactions

Database file:

```text
database/hotel.db
```

---

## 🔐 Data Management

The system maintains structured records for hotel operations and reduces dependency on manual paperwork.

The database allows the application to retrieve and manage billing and customer information efficiently.

---

## 💡 Advantages

* Easy-to-use interface
* Faster billing
* Reduced calculation errors
* Digital record keeping
* Centralized hotel management
* Easy access to previous bills
* Better organization of customer information
* Reduced paperwork

---

## 🔮 Future Enhancements

The following features can be added in future versions:

* Online food ordering
* Online table reservation
* QR-code based menu
* UPI/payment gateway integration
* GST invoice generation
* Employee management
* Inventory management
* Customer feedback system
* Email/SMS bill notifications
* Advanced sales analytics
* Cloud database integration
* Role-based authentication for Admin and Staff

---

## 📸 Screenshots

Add screenshots of your application here:

```text
screenshots/
├── dashboard.png
├── billing.png
├── menu.png
├── customers.png
├── tables.png
├── reservations.png
├── bill-history.png
└── reports.png
```

Example:

```markdown
![PetPuja Dashboard](screenshots/dashboard.png)
```

---

## 👩‍💻 Developer

**Payal Gawade**

B.Tech – Artificial Intelligence & Data Science

---

## 📄 License

This project is developed for **academic/educational purposes**.

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.
