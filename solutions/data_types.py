class Resource:
    def __init__(self, data):
        self.id = data['resource']['id']
        if 'active' in data['resource'] and not data['resource']['active']:
            print('Inactive {} found'.format(data['resource']['resourceType']))


class Organization(Resource):
    def __init__(self, data):
        super().__init__(data)
        if len(data['resource']['address']) > 1:
            print('Organization found with more than one address')

        address = data['resource']['address'][0]

        self.country = str(address['country']).lower()
        self.state = str(address['state']).lower()
        self.city = str(address['city']).lower()
        self.post_code = str(address['postalCode'])

        self.name = data['resource']['name']

        self.practitioners = []
        self.patients = []


class Practitioner(Resource):
    def __init__(self, data):
        super().__init__(data)

        self.patients = []
        self.organizations = []


class Patient(Resource):
    def __init__(self, data):
        super().__init__(data)

        self.gender = data['resource']['gender']

        self.practitioner = None
        self.organization = None
        self.encounters = []
        self.observations = []


class Encounter(Resource):
    def __init__(self, data):
        super().__init__(data)

        self.patient = data['resource']['subject']['reference'].split(':')[-1]


class Observation(Resource):
    def __init__(self, data):
        super().__init__(data)

        self.code = data['resource']['code']
        self.value = data['resource'].get('valueQuantity', None)
        self.effective = data['resource']['effectiveDateTime']
        self.component = data['resource'].get('component', [])

        self.encounter = data['resource']['context']['reference'].split('/')[1]
        self.patient = data['resource']['subject']['reference'].split(':')[-1]
