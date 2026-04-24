# Init file for Glamping Viability plugin
def classFactory(iface):
    from .glamping_viability import GlampingViability
    return GlampingViability(iface)
