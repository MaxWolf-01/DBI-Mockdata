from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator


@dataclass
class FakeRecordGenerator(ABC):
    def records(self, n_records: int = 100) -> Iterator[dict]:
        for i in range(n_records):
            yield self.generate_record(i)

    @abstractmethod
    def generate_record(self, idx: int | None = None) -> dict:
        ...
