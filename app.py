from viktor import ViktorController
from viktor.parametrization import ViktorParametrization
from viktor.geometry import SquareBeam 
from viktor.views import GeometryView, GeometryResult
from viktor.parametrization import NumberField
from viktor import Color
from viktor.geometry import Material
from viktor.geometry import Group
from viktor.geometry import LinearPattern
from viktor.parametrization import ColorField
from viktor.parametrization import Text



class Parametrization(ViktorParametrization):
    width = NumberField('Width', min=0, default=30)
    length = NumberField('Width', min=0, default=30)
    floors = NumberField("How many floors", variant='slider', min=10, max=40, default=16) 
    building_color = ColorField("Facade Color", default=Color(221, 221, 221)) 
    intro_text = Text( "# 3D Parametric Building App 🏢\n"
    "In this app, the user can change the dimensions of the building, choose the amount of floors and a color for the facade. The app will generate a 3D building and a carbon footprint for the user as output.")


class Controller(ViktorController):
    label = "Parametric Building"
    parametrization = Parametrization

    @GeometryView("3D building", duration_guess=1)
    def get_geometry(self, params, **kwargs):
        #Materials:
        glass = Material("Glass", color=Color(150, 150, 255))
        facade = Material("Concrete", color=params.building_color) #<-- add color here

        floor_glass = SquareBeam(
            length_x=params.width,
            length_y=params.length,
            length_z=2,                    #<-- change this
            material=glass
            )
        floor_facade = SquareBeam(
            length_x=params.width+1,       #<-- change this
            length_y=params.length+2,      #<-- change this
            length_z=1,
            material=facade
            )

        floor_facade.translate((0, 0, 1.5)) #<-- add this

        floor = Group([floor_glass, floor_facade])

        floor = Group([floor_glass, floor_facade]) #<-- USe this line as a reference!

        building = LinearPattern(floor, direction=[0, 0, 1], number_of_elements=params.floors, spacing=3) 
            
        return GeometryResult(building)

