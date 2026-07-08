from fastapi import FastAPI

from doro.app.doro_reader import DoroReader

app = FastAPI(title="DoroDirector")


class DoroDirector:
    def __init__(self):
        pass 

    def get_data(self):
        w = DoroReader()
        return w.get_data()
        