from nicegui.elements.label import Label as NiceGUILabel

from nicemvvm.observables.Observable import Observer


class Label(NiceGUILabel, Observer):
    def __init__(self, text=""):
        super().__init__(text=text)
