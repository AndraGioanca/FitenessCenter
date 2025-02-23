# Fitness Center Management System

## 1. Project Description
This application serves as a management system for a fitness center, offering functionalities for both administrators and clients. The main features include subscription management, class scheduling, equipment tracking, and feedback collection.

### Features:
- **Client Features:**
  - View available subscription plans.
  - Enroll in fitness classes.
  - View enrolled subscriptions and classes.
  - Submit feedback.

- **Administrator Features:**
  - Manage classes: Add, update, and delete.
  - Monitor subscriptions and user activity reports.
  - Manage equipment: Add, update status, and remove.
  - View and analyze feedback.

## 2. Database Design

### Relational Database Schema
The database consists of the following tables and relationships:

1. **Users:**
   - Stores details about all users (clients and administrators).
   - Primary Key: `UserID`.

2. **Subscriptions:**
   - Stores available subscription plans for clients.
   - Primary Key: `SubscriptionID`.

3. **Classes:**
   - Stores details about fitness classes.
   - Linked to `Trainers` table.
   - Primary Key: `ClassID`.

4. **Trainers:**
   - Stores trainer information.
   - Primary Key: `TrainerID`.

5. **Equipment:**
   - Stores details about gym equipment.
   - Primary Key: `EquipmentID`.

6. **ClassDetails:**
   - Tracks users enrolled in classes.
   - Composite Primary Key: (`UserID`, `ClassID`).

7. **EquipmentUsage:**
   - Tracks equipment usage by users.
   - Composite Primary Key: (`UserID`, `EquipmentID`, `UsageDate`).

8. **Feedback:**
   - Stores user-submitted feedback.
   - Primary Key: `FeedbackID`.

9. **UserDetails:**
   - Denormalized table storing subscription and class details.
   - Primary Key: `DetailID`.

### Integrity Constraints
- **Foreign Keys:** Ensure relational integrity between tables.
- **Validation Rules:** Prevent invalid data entry (e.g., `Equipment` statuses must be `functional` or `under maintenance`).

### Database Schema Diagram
- `Users` → `ClassDetails` and `Feedback`
- `Classes` → `Trainers` and `ClassDetails`
- `Equipment` → `EquipmentUsage`
- `Subscriptions` → `UserDetails`

## 3. Application Functionality

### Client Interface
- **Dashboard:** Quick access to all client functionalities.
- **View Classes:** Display available and enrolled classes.
- **My Subscription:** View active subscription details.
- **Submit Feedback:** Direct feedback submission.

### Admin Interface
- **Manage Classes:** Add, edit, delete, and track class enrollments.
- **Manage Subscriptions:** View and analyze user subscription activity.
- **Manage Equipment:** Add, update, and remove gym equipment.
- **Feedback Analysis:** Review and analyze user feedback.

## 4. Table Descriptions

### Users Table
| Column    | Type         | Description                          |
|-----------|-------------|--------------------------------------|
| `UserID`  | INT         | Unique identifier for each user.    |
| `Username` | VARCHAR(50) | Login username.                     |
| `Password` | VARCHAR(255)| Encrypted password.                 |
| `Role`     | VARCHAR(10) | User role (`client` or `admin`).    |
| `Name`     | VARCHAR(100)| Full name of the user.              |

### Subscription Table
| Column       | Type         | Description                           |
|-------------|-------------|---------------------------------------|
| `SubscriptionID` | INT       | Unique identifier for subscriptions. |
| `Type`      | VARCHAR(10) | Subscription type (`strength`, `cardio`, etc.). |
| `Price`     | DECIMAL     | Subscription cost. |

(Other tables follow a similar format.)

## 5. Integrity Constraints
- **Primary Keys:** Ensure unique record identification.
- **Foreign Keys:** Maintain relational integrity.
- **Validation Rules:** Enforce valid data entry.

## 6. Technologies Used
- **Backend:** Python (Flask)
- **Database:** SQL Server
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git & GitHub

## 7. Conclusion
This Fitness Center Management System efficiently handles user subscriptions, class scheduling, equipment usage, and feedback collection. It is designed for easy navigation and management for both clients and administrators.


