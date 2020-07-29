import json
import os
from os.path import join as J
from typing import List

from .data_types import *


def read_dataset(dataset_path):
    files = list(filter(lambda x: x.endswith('json'), os.listdir(dataset_path)))

    organizations = {}
    practitioners = {}
    patients = {}
    encounters = {}
    observations = {}

    for file in files:
        print('Reading file', file)

        with open(J(dataset_path, file), 'r') as f:
            bundle_group = json.loads(f.read())['entry']

        for bundle in bundle_group:
            local_organizations = list(filter(lambda x: x['resource']['resourceType'] == 'Organization', bundle['entry']))
            local_practitioners = list(filter(lambda x: x['resource']['resourceType'] == 'Practitioner', bundle['entry']))
            local_patients = list(filter(lambda x: x['resource']['resourceType'] == 'Patient', bundle['entry']))
            local_encounters = list(filter(lambda x: x['resource']['resourceType'] == 'Encounter', bundle['entry']))
            local_observations = list(filter(lambda x: x['resource']['resourceType'] == 'Observation', bundle['entry']))

            if len(local_organizations) > 1:
                print("Oh no. More than one organization in bundle.")
            if len(local_practitioners) > 1:
                print("Oh no. More than one practitioner in bundle.")
            if len(local_patients) > 1:
                print("Oh no. More than one patient in bundle.")

            local_organization: Organization = Organization(local_organizations[0])
            local_practitioner: Practitioner = Practitioner(local_practitioners[0])
            local_patient: Patient = Patient(local_patients[0])
            local_encounters: List[Encounter] = list(map(Encounter, local_encounters))
            local_observations: List[Observation] = list(map(Observation, local_observations))

            if local_organization.id not in organizations:
                organizations[local_organization.id] = local_organization
            else:
                local_organization = organizations[local_organization.id]

            if local_practitioner.id not in practitioners:
                practitioners[local_practitioner.id] = local_practitioner
            else:
                local_practitioner = practitioners[local_practitioner.id]

            if local_patient.id not in patients:
                patients[local_patient.id] = local_patient
            else:
                print("Oh no. Duplicate patient.")
                local_patient = patients[local_patient.id]

            local_patient.organization = local_organization.id
            local_patient.practitioner = local_practitioner.id
            local_patient.observations = list(map(lambda x: x.id, local_observations))
            local_patient.encounters = list(map(lambda x: x.id, local_encounters))
            local_organization.patients.append(local_patient.id)
            local_practitioner.patients.append(local_patient.id)

            if local_practitioner.id not in local_organization.practitioners:
                local_organization.practitioners.append(local_practitioner.id)
            if local_organization.id not in local_practitioner.organizations:
                local_practitioner.organizations.append(local_organization.id)

            for local_encounter in local_encounters:
                if local_encounter.id in encounters:
                    print("Oh no. Duplicate encounter.")
                if local_encounter.patient != local_patient.id:
                    print("Oh no. Encounter patient id does not match with bundle patient.")
                encounters[local_encounter.id] = local_encounter

            local_encounters_ids = list(map(lambda x: x.id, local_encounters))
            for local_observation in local_observations:
                if local_observation.id in observations:
                    print("Oh no. Duplicate encounter.")
                if local_observation.patient != local_patient.id:
                    print("Oh no. Observation patient id does not match with bundle patient.")
                if local_observation.encounter not in local_encounters_ids:
                    print("Oh no. Observation encounter not found in bundle.")

                observations[local_observation.id] = local_observation

    print("Read data:\n{} Organizations\n{} Practitioners\n{} Patients\n{} Encounters\n{} Observations".format(
        len(organizations),
        len(practitioners),
        len(patients),
        len(encounters),
        len(observations)
    ))

    return {
        'organizations': organizations,
        'practitioners': practitioners,
        'patients': patients,
        'encounters': encounters,
        'observations': observations
    }
