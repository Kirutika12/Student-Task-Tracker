# Student Task Tracker

A simple and user-friendly web application that helps students organize, manage, and track their daily academic tasks.

## 🌐 Live Demo

[Open Student Task Tracker](https://student-task-tracker-roan.vercel.app)

## ✨ Features

- User Registration and Login
- Secure Password Hashing
- Add New Tasks
- Edit Existing Tasks
- Delete Tasks
- Mark Tasks as Completed
- Set Task Priorities (High, Medium, Low)
- Individual Task Management for Each User
- PostgreSQL Database Integration

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS
- **Backend:** Python, Flask
- **Database:** PostgreSQL (Neon)
- **Deployment:** Vercel
- **Version Control:** Git and GitHub

## 📁 Project Structure

```text
Student-Task-Tracker/
│
├── public/
│   └── static/
│       └── style.css
│
├── templates/
│   ├── index.html
│   ├── login.html
│   └── register.html
│
├── app.py
├── database.py
├── requirements.txt
└── .gitignore
```

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Kirutika12/Student-Task-Tracker.git
```

### 2. Open the project folder

```bash
cd Student-Task-Tracker
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root directory:

```env
DATABASE_URL=your_neon_pooled_connection_string
SECRET_KEY=your_secret_key
```

Replace the example values with your own credentials. Never upload your `.env` file to GitHub.

### 5. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## ☁️ Deployment

The application is deployed using Vercel and uses Neon PostgreSQL for database storage.

**Live URL:** https://student-task-tracker-roan.vercel.app

## 🎯 Project Objective

The main objective of this project is to help students manage their academic activities efficiently by providing a simple platform to create, organize, update, and track tasks.

## 👩‍💻 Developer

**Kirutika K R**

---

⭐ If you find this project useful, feel free to explore the repository!
