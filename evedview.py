from nicegui import ui, context


@ui.page("/")
async def index():
    context.client.content.classes("p-0")

    ui.page_title("eVED Viewer")
    ui.label("Hello from eved-view!")


ui.run()
