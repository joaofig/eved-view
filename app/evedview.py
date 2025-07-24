from nicegui import context, ui, app

from app.models.trip import TripModel
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
    """)

    app.add_static_files("/js", "app/js")

    ui.add_head_html('''
    <link rel="stylesheet" href="/js/leaflet/contextmenu/leaflet.contextmenu.css"/>
    ''')
    #
    # ui.add_body_html('''
    # <script type="text/javascript">
    #     function map_demo(e) {
    #         alert("map_demo");
    #     }
    # </script>
    # ''')

    context.client.content.classes("p-0")
    ui.page_title("eVED Viewer")
    MainView()


def setup_app():
    locator = ResourceLocator()
    locator["TripModel"] = TripModel()


setup_app()
ui.run()
