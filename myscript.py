# myscript.py
from pathlib import Path

import exrex  # optional for generating with regex
import numpy as np  # optional
from faker import Faker

from exporter import CSVExporter
from generator import FakeRecordGenerator

faker = Faker()


class MyFakeGenerator(FakeRecordGenerator):
    def generate_record(self, idx: int | None = None) -> dict:
        return {
            "id": idx,
            "first_name": faker.first_name(),
            "grade": np.random.choice(list('12345'), p=[0.1, 0.2, 0.4, 0.2, 0.1]),
            "class": exrex.getone("[1-5][A-C](HIF|FIT|HKUI)"),
        }


f = MyFakeGenerator()
CSVExporter.export(
    records=f.records(n_records=10),
    headers=f.generate_record(0).keys(),
    path=Path("out", "my_file.csv")
)
