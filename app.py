import requests
from viktor import ViktorController
from viktor.parametrization import ViktorParametrization
from viktor.geometry import SquareBeam 
from viktor.views import GeometryView, GeometryResult, GeometryAndDataResult, GeometryAndDataView, DataGroup, DataItem
from viktor.parametrization import NumberField, OptionField, AutocompleteField
from viktor import Color
from viktor.geometry import Material
from viktor.geometry import Group
from viktor.geometry import LinearPattern
from viktor.parametrization import ColorField
from viktor.parametrization import Text

dev_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDAyMDg3MzUsImV4cCI6MjAxNTU2ODczNSwidG9rZW5fdHlwZSI6ImRldmVsb3Blcl9hY2Nlc3MiLCJmaXJzdF9uYW1lIjoiUGhhbm9zIiwibGFzdF9uYW1lIjoiSGFkamlreXJpYWtvdSIsIm9jY3VwYXRpb24iOiJPdGhlciIsInVzZXJfY29tcGFueSI6IjIwNTAgTWF0ZXJpYWxzIiwidXNlcl9lbWFpbCI6InBoYW5vc0AyMDUwLW1hdGVyaWFscy5jb20ifQ.rrtPvZgV51oZFuWA2N-Ry5j7rO1zo_zcTQsaYVN7FIQ'
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
    width = NumberField('Width', min=0, default=30)
    length = NumberField('Length', min=0, default=40)
    floors = NumberField("How many floors", variant='slider', min=10, max=40, default=16) 
    glazing_ratio = NumberField("Glazing Ratio", variant='slider', min=1, max=99, default=50) 
    typology = AutocompleteField('Typology options', 
                                 options=["Residential, High-rise", "Residential, Low-rise", "Commercial, High-rise", "Commercial, Low-rise", "Commercial, Fitout", "Industrial, Low-rise", "Farm building", "Outhouse", "School", "Garage", "Cultural building, Low-rise", "Retail (supermarket), Low-rise", "Carport, Low-rise", "Office, High-rise", "Daycare institution, Low-rise", "Detached house", "Factory, Low-rise", "Hospital, Low-rise", "Logistic, High-rise", "Hotel, High-rise", "Multi dwelling, High-rise", "Office (residential building), High-rise", "Sport centre"], 
                                 default='Commercial, High-rise')
    material_choice = AutocompleteField('Material options', 
                                options=["Low-carbon, Regenerative materials", "Conventional materials", "High-carbon (Metal, Concrete)"], 
                                default="Conventional materials")



    building_color = ColorField("Facade Color", default=Color(221, 221, 221)) 
    intro_text = Text( "# 3D Parametric Building App 🏢\n"
    "In this app, the user can change the dimensions of the building, choose the amount of floors and a color for the facade. The app will generate a 3D building and a carbon footprint for the user as output.")


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

        wp_calculated = get_embodied_carbon_and_warming_potential(dev_token=dev_token, building_type=params.typology, glazing_percentage=params.glazing_ratio, gross_internal_floor_area=gia, materials_type=params.material_choice, stories=params.floors)
        wp_calculated_datagroup = DataGroup(DataItem('Embodied Carbon (kgCO2e/m2 GIA)',wp_calculated['co2e_per_m2']),DataItem('Warming Potential (°C)',wp_calculated['warming_potential']))

        return GeometryAndDataResult(building, data=wp_calculated_datagroup, labels=)

