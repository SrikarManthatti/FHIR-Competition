Each patient has exactly one practitioner and exactly one organization
Each practitioner may belong to many organizations

Each JSON file should contain a single entry object (not an array of entries).

Dataset will be built in `dataset` folder in the root directory, with this file structure:
```
dataset/
    organization{organization_id}/
        organization{organization_id}.json
        practitioner{practitioner_id}/
            practitioner{practitioner_id}.json
            patient{patient_id}/
                patient{patient_id}.json
                observation{observation_id}.json
                other_resources{resource_id}.json

            another_patient{another_patient_id}/
                another_patient{another_patient_id}.json
                ...
                ...

        another_practitioner{another_practitioner_id}/
            another_practitioner{another_practitioner_id}.json
            ...
            ...

    another_organization{another_organization_id}/
        another_organization{another_organization_id}.json
        ...
        ...
```