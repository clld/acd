from clld_cognacy_plugin.adapters import GeoJsonCognateset


class GeoJsonReconstruction(GeoJsonCognateset):
    def feature_properties(self, ctx, req, valueset):
        values = [co.counterpart for co in ctx.cognates]
        return {
            'label': '{}: {}'.format(
                self.get_language(ctx, req, valueset).name,
                ', '.join(v.name for v in valueset.values if v in values and v.name)),
        }


def includeme(config):
    pass
