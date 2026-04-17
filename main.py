from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='Patient ID', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='Living city of the patient')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['Male','Female'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(...,gt=0,description='Height of the patient in meter')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kg')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi <25:
            return 'Normal'
        elif self.bmi <30:
            return 'Normal'
        else:
            return 'Overweight'

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(..., description='Name of the patient')]
    city: Annotated[Optional[str], Field(..., description='Living city of the patient')]
    age: Annotated[Optional[int], Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Optional[Literal['Male','Female']], Field(..., description='Gender of the patient')]
    height: Annotated[Optional[float], Field(...,gt=0,description='Height of the patient in meter')]
    weight: Annotated[Optional[float], Field(..., gt=0, description='Weight of the patient in kg')]


def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data


def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)


@app.get("/")
def hello():
    return {
        'message':'Patient Management System FastAPI'
    }

@app.get('/about')
def about():
    return {
        'message':'A fully functional api to manage patient records'
    }

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    #load all patient data
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found!')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight, bmi'), order: str = Query('asc', description='Sort in asc or dsc order')):
    valid_fileds = ['height','weight','bmi']
    if sort_by not in valid_fileds:
        raise HTTPException(status_code=400, detail=f'invalid field select from {valid_fileds}')
    order_by = ['asc', 'desc']
    if order not in order_by:
        raise HTTPException(status_code=400, detail=f'invalid order select between asc and dsc')
    
    data = load_data()
    sort_order = True if order=='desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data


@app.post('/create')
def create_patient(patient:Patient):
    #load existing data
    data = load_data()
    # check if the patient already exist
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exist')
    # new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save into json file
    save_data(data)
    return JSONResponse(status_code=201, content={'message':'Patient Created Successfully'})


@app.put('/edit/{patient_id}')
def update_patient(patinet_id:str,patient_update:PatientUpdate):
    data = load_data()
    if patinet_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found!')
    existing_patient_info = data[patinet_id]