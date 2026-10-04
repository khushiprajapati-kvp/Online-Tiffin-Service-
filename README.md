# OTS - Online Tiffin Service

OTS is a Flask web application for an online tiffin service. Customers can browse meals, create an account, place bookings, track orders, and leave ratings. Admin and delivery-staff pages support menu, staff, booking, and customer management.

## Features

- Customer registration and login
- Meal menu with images and descriptions
- Tiffin booking and order status management
- Admin dashboard, reports, and menu/staff management
- Delivery staff dashboard
- Contact messages and customer ratings

## Tech stack

- Python and Flask
- MySQL
- PyMySQL
- HTML, CSS, and Jinja templates

## Requirements

- Python 3.8 or newer
- MySQL Server

## Local setup (Windows)

1. Clone or download this repository and open a terminal in the project folder.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the Python dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Create a MySQL database:

   ```sql
   CREATE DATABASE ots CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. Import `database/ots.sql` into the `ots` database using MySQL Workbench (Server > Data Import), or from Command Prompt with `mysql -u root -p ots < database\ots.sql`. The SQL file recreates the application's tables and includes the menu catalogue. Import it only into a new or disposable database: it contains `DROP TABLE` statements.
6. Copy the environment template and edit `.env` with your local settings:

   ```powershell
   Copy-Item .env.example .env
   ```

   Set `SECRET_KEY` to a long random value and update the MySQL settings if needed. Keep `.env` private; it is excluded from Git.
7. Start the application:

   ```powershell
   py app.py
   ```

8. Open <http://127.0.0.1:5500/>.

## First admin account

The schema does not include accounts or personal data. Create the first admin account yourself in MySQL Workbench after importing the schema:

```sql
INSERT INTO admin (name, email, password)
VALUES ('Site Admin', 'admin@example.com', 'replace-with-a-unique-password');
```

Replace all example values before running this statement. Customers can register from the website; add staff through the admin pages.

## Configuration

The application reads these variables from `.env`:

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | Required | Flask session-signing key |
| `DB_HOST` | `localhost` | MySQL server host |
| `DB_PORT` | `3306` | MySQL server port |
| `DB_NAME` | `ots` | Database name |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | Empty | MySQL password |
| `FLASK_DEBUG` | `false` | Set to `true` for local debugging only |
| `PORT` | `5500` | Local web-server port |

## Notes

- Password handling in the current application is not suitable for production; do not use real customer credentials or deploy it as-is to a public service.
- Do not commit `.env`, database exports containing real data, or uploaded files that contain private information.
- The original Word document under `Documentation/` is excluded from Git because it contains sample login credentials and contact details.
