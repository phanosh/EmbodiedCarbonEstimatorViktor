from viktor import ViktorController
from viktor.parametrization import ViktorParametrization
from viktor.geometry import SquareBeam 
from viktor.views import GeometryView, GeometryResult



class Parametrization(ViktorParametrization):
    pass


class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization


class Controller(ViktorController):
    label = "your entity type"
    parametrization = Parametrization

    @GeometryView("3D Geometry", duration_guess=1)
    def get_geometry(self, params, **kwargs):
        block = SquareBeam(
            length_x=1,
            length_y=1,
            length_z=1
        )
        return GeometryResult(block)
