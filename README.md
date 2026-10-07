# Parking Management System (DBMS)

A web-based Parking Management System built with **Flask (Python)** and **MySQL**, designed to streamline parking slot allocation, entry/exit ticketing, and administrative monitoring.

## 🚀 Features

- **User Entry & Slot Booking**: Register vehicle details and select available parking slots across different floors.
- **Real-Time Slot Availability**: Dynamic slot status visualization (Available vs Occupied) by vehicle type (Car, Bike, Truck).
- **Admin Dashboard**: Overview of parking occupancy, pending parking requests, vehicle logs, and approvals.
- **Admin Exit & Billing**: Manage vehicle checkout with automated fee calculation and printable receipt slips.
- **SQL Database Integration**: Relational schema handling vehicles, parking slots, requests, and entries with foreign key constraints.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask
- **Database**: MySQL (`mysql-connector-python`)
- **Frontend**: HTML5, CSS3, JavaScript (Jinja2 templates)

---

## 📋 Prerequisites

- Python 3.9+
- MySQL Server (e.g., MySQL 8.x or XAMPP / MariaDB)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Ashutosh-550/Parking-Management-System-DBMS.git
cd Parking-Management-System-DBMS
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
1. Open your MySQL client (Command Line, MySQL Workbench, or phpMyAdmin).
2. Import the database schema and sample data:
   ```bash
   mysql -u root -p < Database.sql
   ```

### 5. Configure Environment Variables
Set your MySQL root password:
```bash
export MYSQL_PASSWORD="your_mysql_password"  # On Windows: set MYSQL_PASSWORD=your_mysql_password
```

### 6. Run the Application
```bash
python3 app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 👥 Default Admin Credentials
- **Username**: `admin2`
- **Password**: `admin123`
*(Configured in `Database.sql`)*
