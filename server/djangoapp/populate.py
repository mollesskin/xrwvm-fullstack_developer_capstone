from .models import CarMake, CarModel


SAMPLE_CARS = {
    "Audi": [("A6", "Sedan"), ("Q5", "SUV")],
    "BMW": [("X5", "SUV"), ("3 Series", "Sedan")],
    "Ford": [("Mustang", "Coupe"), ("Explorer", "SUV")],
    "Honda": [("Civic", "Sedan"), ("CR-V", "SUV")],
    "Toyota": [("Camry", "Sedan"), ("RAV4", "SUV")],
}


def initiate():
    """Populate demonstration makes and models without duplicating rows."""
    for make_name, models in SAMPLE_CARS.items():
        make, _ = CarMake.objects.get_or_create(
            name=make_name, defaults={"description": f"{make_name} vehicles"}
        )
        for model_name, body_type in models:
            CarModel.objects.get_or_create(
                car_make=make, name=model_name, year=2023, defaults={"type": body_type}
            )
