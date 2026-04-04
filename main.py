from fastapi import FastAPI


app = FastAPI()


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