from nicegui import ui, context
from app.views.MainView import MainView


@ui.page("/")
async def index():
    context.client.content.classes("p-0")

    MainView()


ui.run()
