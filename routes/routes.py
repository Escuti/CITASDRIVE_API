from fastapi import APIRouter
from services.patient_service import Patient_Service
from models.patient_model import Patient
from services.appoint_service import Appoint_Service
from models.appoint_model import Appoint

routes_p = APIRouter(prefix="/patient", tags=["Patient"])

patient_service = Patient_Service()
patient_model = Patient

@routes_p.get("/get-patients")
async def get_all_patients():
    return await patient_service.get_patients()

@routes_p.get("/get-patient/{user_id}")
async def get_patient(user_id=int):
    return await patient_service.get_patient_by_id(user_id)

@routes_p.post("/create-patient")
async def create_patient(user: Patient):
    return await patient_service.create_patient(user)

@routes_p.put("/update-patient/{user_id}")
async def update_patient(user_id: int, user_data: Patient):
    return await patient_service.update_patient(user_id, user_data)

@routes_p.delete("/delete-patient/{user_id}")
async def delete_patient(user_id=int):
    return await patient_service.delete_patient(user_id)

routes_a = APIRouter(prefix="/appoints", tags=["Appoint"])

appoint_service = Appoint_Service()
appoint_model = Appoint

@routes_a.get("/get-appoints")
async def get_all_appoints():
    return await appoint_service.get_appoints()

@routes_a.get("/get-appoint/{patient_id}")
async def get_appoint_by_patient(patient_id=int):
    return await appoint_service.get_appoint_by_patient(patient_id)

@routes_a.post("/create-appoint")
async def create_appoint(appoint: Appoint):
    return await appoint_service.create_appoint(appoint)

@routes_a.put("/update-appoint/{appoint_id}")
async def update_appoint(appoint_id: int, appoint_data: Appoint):
    return await appoint_service.update_appoint(appoint_id, appoint_data)

@routes_a.delete("/delete-appoint/{appoint_id}")
async def delete_appoint(appoint_id=int):
    return await appoint_service.delete_appoint(appoint_id)