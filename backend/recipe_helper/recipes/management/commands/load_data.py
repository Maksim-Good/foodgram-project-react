import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "load data from csv"

    def handle(self, *args, **options):
        with open("ingredients.csv", encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                name = row["name"]
                measurement_unit = row["measurement_unit"]
                staff = Ingredient(
                    name=name,
                    measurement_unit=measurement_unit
                )
                staff.save()
        csv_file.close()
        print("Ингридиенты загружены.")
