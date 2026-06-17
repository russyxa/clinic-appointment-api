# Clinic Appointment API

This project is a simple Clinic Appointment API built using FastAPI and Docker.

## Laboratory Context
This project was developed in an offline Windows 11 laboratory environment.
Python was not installed directly on the computer. The application was executed using Docker and a prebuilt Docker image named clinic-fastapi-base:1.0.

## Features
- Create clinic appointments
- View all appointments
- View one appointment
- Update appointment details
- Cancel appointments

## Authentication

This API uses simple bearer-token authentication. The welcome message (`GET /`) and the login endpoint (`POST /login`) are public. All appointment-related endpoints require a valid bearer token.

### Test Account
- Username: `admin`
- Password: `clinic123`
- Token returned on successful login: `clinic-secret-token`

### Login Endpoint
`POST /login`

Send the test account's username and password in the request body. On success, the response contains an `access_token` and `token_type`:

In Swagger UI, click **Authorize** and enter the token to access protected endpoints.

### Protected Endpoints
The following endpoints require the bearer token (`Authorization: Bearer clinic-secret-token`):

| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | /me | View current authenticated user |
| GET | /appointments | View all appointments |
| GET | /appointments/{appointment_id} | View one appointment |
| POST | /appointments | Create an appointment |
| PUT | /appointments/{appointment_id} | Update an appointment |
| DELETE | /appointments/{appointment_id} | Cancel an appointment |

Requests without a token receive a `403 Not authenticated` response. Requests with an invalid or expired token receive a `401 Invalid or expired token` response.

## Technologies Used
- Python
- FastAPI
- Docker
- Git

## How to Run
docker compose up --build

Open http://localhost:8000/docs.
