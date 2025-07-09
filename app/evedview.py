from nicegui import context, ui

from app.models.TripModel import TripModel
from app.views.MainView import MainView
from nicemvvm.ResourceLocator import ResourceLocator


@ui.page("/")
async def index():
    context.client.content.classes("p-0")
    ui.page_title("eVED Viewer")
    MainView()


def setup_app():
    locator = ResourceLocator()
    locator["TripModel"] = TripModel()


setup_app()
ui.run()
