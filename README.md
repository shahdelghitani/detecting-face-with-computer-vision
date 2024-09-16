# Face Recognition Attendance System

## Project Overview
This project is a **Face Recognition Attendance System** that captures a person's image, identifies them, and records their **entry and exit times**. The system recognizes whether it's the user's first appearance and stores their **name** in the database. On subsequent appearances, it uses their **ID** to verify and log attendance.

## Features
- **Capture and Register:** Captures the image of the person and checks if it's their first appearance. If so, their name is stored in the database.
- **Attendance Logging:** Records the entry and exit times for every appearance of the person.
- **No Image Storage:** The captured image is used only for identification purposes and is not stored in the system.

## Tech Stack
- **Backend Framework:** Flask
- **Database:** SQLite
- **Face Recognition Library:** face_recognition (Python)
- **API Testing Tool:** Postman


