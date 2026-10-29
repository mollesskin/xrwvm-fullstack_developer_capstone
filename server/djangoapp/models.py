from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    TYPE_CHOICES = [(value, value) for value in ("Sedan", "SUV", "Wagon", "Coupe", "Hatchback", "Truck")]

    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    year = models.PositiveIntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2023)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["car_make", "name", "year"], name="unique_car_model_year")]

    def __str__(self):
        return f"{self.car_make} {self.name} ({self.year})"
