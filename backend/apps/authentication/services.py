NMC_MOCK_REGISTRY = {
    "12345": {
        "first_name": "Ram Prasad",
        "last_name": "Shah",
        "specialization": "Cardiology"
    },
    "67890": {
        "first_name": "Sita",
        "last_name": "Thapa",
        "specialization": "Pediatrics"
    },
    "99999": {
        "first_name": "Peter",
        "last_name": "Dhungana",
        "specialization": "General Surgery"
    }
}

def verify_nmc_credentials(nmc_number):
    cleaned_number = str(nmc_number).strip()
    return NMC_MOCK_REGISTRY.get(cleaned_number, None)