from nicegui import context, ui

from app.models.TripModel import TripModel
from app.views.main import MainView
from nicemvvm.ResourceLocator import ResourceLocator


@ui.page("/")
async def index():
    ui.add_css("""
    .custom-scroll-area .q-scrollarea__content {
        padding: 0px 12px 0px 4px !important;
        gap: 0px !important;
    }
    .edit-view-field .q-field {
        padding-top: 4px !important;
    }
    .small-menu .q-item {
        min-height: 24px;
        padding: 4px 8px;
        font-size: 12px;
    }
    """)

    context.client.content.classes("p-0")
    ui.page_title("eVED Viewer")
    MainView()


def setup_app():
    locator = ResourceLocator()
    locator["TripModel"] = TripModel()


setup_app()
ui.run()
