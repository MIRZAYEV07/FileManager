
import os

current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)

example = {
    'property': [{'enable': 1}],
    'roi-filtering-stream-0': [{'enable': 1, 
                                'roi-RF': '295;643;600;660;642;913;80;850',
                                'inverse-roi': 1}],
    
}


class Property:
    def __init__(self,  key, value):
        self.key = key
        self.value = value
    
    def generate_property(self):
        return f'{self.key}: {self.value}'


class PropertyApplicationGroup:
    def __init__ (self, name, stream_number, property_list):
        self.stream_number = stream_number
        self.name = name
        self.property_list = property_list
   

    def generate_property_application_group(self):
        property_application_group = f'[{self.name}]\n'
        # remove '' from property_application_group

        for property in self.property_list:
            property_application_group += f'  {property.generate_property()}\n'
        return property_application_group




# function to generate config file
def generate_config_file(config_file_name, config_file_content):
    config_file = open(current_path + config_file_name, 'w')
    config_file.write(config_file_content)
    config_file.close()
