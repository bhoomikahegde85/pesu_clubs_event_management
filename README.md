# PESU Clubs and Event Management System

A comprehensive web application for managing clubs and events at PES University. Built with MySQL for database management and Streamlit for the frontend interface.

## 📋 Features

- **User Authentication**
  - Role-based access control (Club Member, Club Head, Management)
  - Secure login system with password protection
  - Session management

- **Club Management**
  - View and search clubs by name or department
  - Edit club details (for authorized users)
  - Track club membership
  - Associate faculty advisors with clubs
  - Instagram handle management with automatic '@' prefix

- **Event Management**
  - Create and manage club events
  - Track event budgets
  - Schedule events with duration tracking
  - Monitor participant counts

- **Department Integration**
  - Department-wise club organization
  - Faculty advisor assignment
  - Automated email generation for departments

## 🚀 Technology Stack

- **Backend Database**: MySQL 8.0+
- **Frontend**: Streamlit
- **Language**: Python 3.8+
- **Additional Libraries**: 
  - mysql-connector-python
  - pandas
  - dataclasses
  - typing

## ⚙️ Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd pesu-clubs-management
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   - Install MySQL Server
   - Run the SQL scripts in this order:
     ```bash
     mysql -u root -p < pesu_clubs_event_management.sql
     ```

4. **Configure Database Connection**
   - Update the `DB_CONFIG` in the code with your MySQL credentials:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'database': 'pesu_clubs_event_management',
         'user': 'your_username',
         'password': 'your_password',
     }
     ```

## 🔧 Database User Setup

Create the following MySQL users with appropriate permissions:

```sql
-- For management role
CREATE USER 'management'@'localhost' IDENTIFIED BY 'Management@123';
GRANT ALL PRIVILEGES ON pesu_clubs_event_management.* TO 'management'@'localhost';

-- For club heads
CREATE USER 'club_head'@'localhost' IDENTIFIED BY 'ClubHead@123';
GRANT SELECT, UPDATE ON pesu_clubs_event_management.* TO 'club_head'@'localhost';

-- For viewers/club members
CREATE USER 'viewer'@'localhost' IDENTIFIED BY 'Viewer@123';
GRANT SELECT ON pesu_clubs_event_management.* TO 'viewer'@'localhost';
```

## 🚦 Running the Application

1. **Start the Streamlit Server**
   ```bash
   streamlit run app.py
   ```

2. **Access the Application**
   - Open your web browser
   - Navigate to `http://localhost:8501`

## 👥 User Roles and Permissions

1. **Management**
   - Full access to all features
   - Can create/edit/delete clubs and events
   - Can manage faculty advisors

2. **Club Head**
   - Can edit their own club details
   - Can manage events for their club
   - Can view all club information

3. **Club Member**
   - Can view club information
   - Can view event details
   - Read-only access

## 🔒 Default Login Credentials

```
Management:
- Email: eshvar@example.com
- Password: password_3

Club Head:
- Email: adithya@example.com
- Password: password_2

Club Member:
- Email: bhoomika@example.com
- Password: password_1
```

## 🗄️ Database Structure

The system uses the following main tables:
- DEPARTMENT
- FACULTY_ADVISOR
- CLUB
- CLUB_MEMBER
- USERS
- EVENT
- Various log tables for tracking changes

## 🛠️ Maintenance

- Regular database backups recommended
- Monitor log tables for changes
- Update user passwords periodically
- Keep MySQL and Python dependencies updated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

