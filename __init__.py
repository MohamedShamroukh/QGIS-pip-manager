from .my_pip_manager_plugin import MyPipManagerPlugin

def classFactory(iface):
    """Instantiates the plugin class."""
    return MyPipManagerPlugin(iface)