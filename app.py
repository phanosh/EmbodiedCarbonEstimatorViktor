import requests
from viktor import ViktorController
from viktor.parametrization import ViktorParametrization, LineBreak, Image
from viktor.geometry import SquareBeam 
from viktor.views import GeometryView, GeometryResult, GeometryAndDataResult, GeometryAndDataView, DataGroup, DataItem, Label
from viktor.parametrization import NumberField, OptionField, AutocompleteField, TextField
from viktor import Color
from viktor.geometry import Material, Point
from viktor.geometry import Group
from viktor.geometry import LinearPattern
from viktor.parametrization import ColorField
from viktor.parametrization import Text

def get_embodied_carbon_and_warming_potential(dev_token, building_type, glazing_percentage, gross_internal_floor_area, materials_type, stories):
    # Get API token
    url = "https://app.2050-materials.com/developer/api/getapitoken/"
    headers = {'Authorization': f'Bearer {dev_token}'}
    response = requests.get(url, headers=headers)
    response_dict = response.json()
    api_token = response_dict['api_token']

    # Get CO2 Warming Potential
    url_wp = "https://app.2050-materials.com/developer/api/get_co2_warming_potential"
    query_params = {
        'building_type': building_type,
        'glazing_percentage': glazing_percentage,
        'gross_internal_floor_area': gross_internal_floor_area,
        'materials_type': materials_type,
        'stories': stories
    }
    headers['Authorization'] = f'Bearer {api_token}'  # Reuse headers, update the token
    wp_response = requests.get(url_wp, headers=headers, params=query_params)
    wp_response_dict = wp_response.json()
    warming_potential = round(wp_response_dict['warming_potential'], 1)
    co2e_per_m2 = round(wp_response_dict['co2e_per_m2'], 1)

    return {'co2e_per_m2': co2e_per_m2, 'warming_potential': warming_potential}



class Parametrization(ViktorParametrization):
    img = Image(path="logo.png", max_width=200, align='center')
    intro_text = Text( "# 3D Parametric Building App 🏢\n"
                      "This app was developed by [2050 Materials](https://2050-materials.com/sustainability-data-api/). To use the full functionality, please generate a developer token on your account page on the 2050 Materials [Platform](https://app.2050-materials.com/accounts/edit-account/).")
    info_text = Text("2050 Materials aims to integrate sustainability into construction by creating a comprehensive database of building materials' climate impact. Our platform supports real-time environmental impact assessments, facilitating greener building practices. For feedback, please visit [2050 Materials Feedback Form](https://app.2050-materials.com/contact/).")
    main_text = Text("In this app, the user can change the dimensions of the building, choose the amount of floors and a color for the facade. The app will generate a 3D building and a carbon footprint for the user as output.")

    dev_token = TextField('2050 Materials Developer Token', flex=70)
    lb1 = LineBreak()

    width = NumberField('Width', min=0, default=30)
    length = NumberField('Length', min=0, default=40)
    lb2 = LineBreak()

    floors = NumberField("How many floors", variant='slider', min=10, max=40, default=16) 
    glazing_ratio = NumberField("Glazing Ratio", variant='slider', min=1, max=99, default=50) 
    lb3 = LineBreak()

    typology = AutocompleteField('Typology options', 
                                 options=["Residential, High-rise", "Residential, Low-rise", "Commercial, High-rise", "Commercial, Low-rise", "Commercial, Fitout", "Industrial, Low-rise", "Farm building", "Outhouse", "School", "Garage", "Cultural building, Low-rise", "Retail (supermarket), Low-rise", "Carport, Low-rise", "Office, High-rise", "Daycare institution, Low-rise", "Detached house", "Factory, Low-rise", "Hospital, Low-rise", "Logistic, High-rise", "Hotel, High-rise", "Multi dwelling, High-rise", "Office (residential building), High-rise", "Sport centre"], 
                                 default='Commercial, High-rise')
    material_choice = AutocompleteField('Material options', 
                                options=["Low-carbon, Regenerative materials", "Conventional materials", "High-carbon (Metal, Concrete)"], 
                                default="Conventional materials")

    building_color = ColorField("Facade Color", default=Color(221, 221, 221)) 

class Controller(ViktorController):
    label = "Parametric Building"
    parametrization = Parametrization

    @GeometryAndDataView("3D building", duration_guess=1)
    def get_geometry_data_view(self, params, **kwargs):
        #Materials:
        glass = Material("Glass", color=Color(150, 150, 255))
        facade = Material("Concrete", color=params.building_color) #<-- add color here

        glass_height = (params.glazing_ratio/100)*4
        facade_height = (1 - params.glazing_ratio/100)*2

        floor_glass = SquareBeam(
            length_x=params.width,
            length_y=params.length,
            length_z=glass_height,                    
            material=glass
            )
        floor_facade = SquareBeam(
            length_x=params.width+1,       
            length_y=params.length+1,      
            length_z=facade_height,
            material=facade
            )

        floor_facade.translate((0, 0, 1.5)) #<-- add this
        floor = Group([floor_glass, floor_facade])

        building = LinearPattern(floor, direction=[0, 0, 1], number_of_elements=params.floors, spacing=3) 
        gia = params.width * params.length * params.floors
        if params.dev_token:
            wp_calculated = get_embodied_carbon_and_warming_potential(dev_token=params.dev_token, building_type=params.typology, glazing_percentage=params.glazing_ratio, gross_internal_floor_area=gia, materials_type=params.material_choice, stories=params.floors)
            wp_calculated_datagroup = DataGroup(DataItem('Embodied Carbon (kgCO2e/m2 GIA)',wp_calculated['co2e_per_m2']),DataItem('Warming Potential (°C)',wp_calculated['warming_potential']))
        else:
            wp_calculated_datagroup = DataGroup(DataItem('Requires Token from 2050 Materials',None))
        return GeometryAndDataResult(building, data=wp_calculated_datagroup)

