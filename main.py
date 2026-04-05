from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()
def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data

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
