from fastapi import FastAPI, HTTPException, status, Depends 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from secrets import compare_digest 
  
from app.models import AppointmentCreate, AppointmentUpdate, LoginRequest, TokenResponse 

app = FastAPI( 
    title="Clinic Appointment API with Authentication", 
    description="A simple authenticated API for managing clinic appointments.", 
    version="2.0.0" 
) 
  
security = HTTPBearer() 
  
appointments = {} 
next_id = 1 
  
USERS = {
    "admin": {
        "password": "clinic123",
        "role": "clinic_staff",
        "token": "clinic-secret-token"
    },
    "staff": {
        "password": "staff123",
        "role": "clinic_assistant",
        "token": "staff-secret-token"
    }
}
  
  
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    for username, user in USERS.items():
        if compare_digest(token, user["token"]):
            return {
                "username": username,
                "role": user["role"]
            }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token"
    )
  
  
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Clinic Appointment API",
        "version": "2.0.0",
        "authentication": "Bearer token required for appointment endpoints",
        "docs": "/docs"
    }


@app.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    user = USERS.get(login_data.username)

    if user is None or not compare_digest(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return {
        "access_token": user["token"],
        "token_type": "bearer",
        "role": user["role"]
    }


@app.get("/me")
def get_current_user(current_user: dict = Depends(verify_token)):
    return {
        "message": "Authenticated user",
        "user": current_user
    }


@app.get("/appointments")
def get_appointments(current_user: dict = Depends(verify_token)):
    return {
        "count": len(appointments),
        "appointments": appointments
    }


@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: int, current_user: dict = Depends(verify_token)):
    if appointment_id not in appointments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return appointments[appointment_id]


@app.post("/appointments", status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, current_user: dict = Depends(verify_token)):
    global next_id

    new_appointment = {
        "id": next_id,
        "patient_name": appointment.patient_name,
        "doctor_name": appointment.doctor_name,
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "reason": appointment.reason,
        "status": "scheduled",
        "created_by": current_user["username"]
    }

    appointments[next_id] = new_appointment
    next_id += 1

    return {
        "message": "Appointment created successfully",
        "appointment": new_appointment
    }


@app.put("/appointments/{appointment_id}")
def update_appointment(appointment_id: int, appointment_update: AppointmentUpdate, current_user: dict = Depends(verify_token)):
    if appointment_id not in appointments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    existing_appointment = appointments[appointment_id]
    update_data = appointment_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        existing_appointment[key] = value

    existing_appointment["updated_by"] = current_user["username"]
    appointments[appointment_id] = existing_appointment

    return {
        "message": "Appointment updated successfully",
        "appointment": existing_appointment
    }


@app.delete("/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int, current_user: dict = Depends(verify_token)):
    if current_user["role"] != "clinic_staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clinic staff may cancel appointments"
        )

    if appointment_id not in appointments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    appointments[appointment_id]["status"] = "cancelled"
    appointments[appointment_id]["cancelled_by"] = current_user["username"]

    return {
        "message": "Appointment cancelled successfully",
        "appointment": appointments[appointment_id]
    }

