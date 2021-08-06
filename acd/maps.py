from clld_cognacy_plugin.maps import CognatesetMap


class ReconstructionMap(CognatesetMap):
    def get_default_options(self):
        res = CognatesetMap.get_default_options(self)
        res['show_labels'] = False
        res['max_zoom'] = 10
        res['base_layer'] = 'Esri.WorldPhysical'
        return res
