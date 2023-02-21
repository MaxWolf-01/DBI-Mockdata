""" Arbeitsauftrag Schüler-Liste (Formulas mit Mockaroo)
Generiere folgende Testdaten
1) ID (autoincrement)
2) FamName in Upper Case
2) Vorname: abhängig von Geschlecht Vorname Male oder Female (Hilfsspalte)
3) Geschlecht: importiere eine Liste mit den derzeit gültigen Geschlechtsbezeichnungen und verteile diese Zuteilungen so, dass ca 10-15% ein Geschlecht <> Männl/weiblich haben.
4) Geburtsdatum mit einem Alter in der Range von 14 bis 20 Jahren, formatiert als Y-m-d
7) Klasse1: Zuweisung zu einer Klasse entsprechend der Verteilungen aus dem File.
ÄNDERUNG DES GEBURTSDATUMS (soll sich an der Klasse orientieren, dh in der 1.Klasse soll das Geburtsjahr -14 oder -15 betragen, 2.Klasse -15 oder -16 usw.
7b) Klasse mittels Regex: es reicht die Zuteilung zu nur 3 Abteilungen mit 3 Zügen (a, b, c) zu 5 Jahrgängen.
5) ID im Format der Spengergasse, also 3 Stellen des Familiennamen und danach eine Zahl, die von der Klasse abhängig ein Inskriptionsjahr ergibt (zB Klasse = 1, aktuelles Jahr 23 => 22 inskribiert), danach eine Zufallszahl zwischen 0 und 9999 (padding beachten!)
6) e-mail: Schüler-ID @spengergasse.at
8) Notenschnitt je Klasse (regex-Variante) abhängig vom Jahrgang. HIF Notenschnitt bei 2.5 mit einer Streuung von 1.2, FIT 3.0, Streuung 1, die anderen mit einem nach Wahl, Streuung 0.5.
9) Exportieren des Files und Überprüfen der Frequenzen in den Klassen und der Streuungen (zB mit Excel)
"""
from enum import Enum
from pathlib import Path
from typing import TypeVar

import exrex
import numpy as np
import pandas as pd
from faker import Faker
from pandas import DataFrame
from scipy.stats import truncnorm

from exporter import CSVExporter
from generator import FakeRecordGenerator

T = TypeVar('T')

fake = Faker()


class Gender(str, Enum):  # python 3.10 no StrEnum
    maennlich = 'maennlich'
    weiblich = 'weiblich'
    divers = 'divers'
    inter = 'inter'
    offen = 'offen'


class Departments(str, Enum):
    HIF = 'HIF'
    FIT = 'FIT'
    HBGM = 'HBGM'
    HKUI = 'HKUI'


class SchuelerListeRecordGenerator(FakeRecordGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.classes_info: DataFrame = pd.read_excel('data/bearbeitet_Klassenuebersicht.xlsx')

        # for ex 7
        self.student_count_prob_dist_per_class = self.classes_info['Summe'].to_numpy() / self.classes_info[
            'Summe'].sum()
        self.male_percentage_per_class = self.classes_info['m'].to_numpy() / self.classes_info['Summe'].to_numpy()
        # probability distribution for a student being assigned to a specific class based on the number of students per
        # class and the male / female distribution per class
        self.class_prob_x_male_prob = self.student_count_prob_dist_per_class * self.male_percentage_per_class
        self.class_prob_x_female_prob = self.student_count_prob_dist_per_class * (1 - self.male_percentage_per_class)
        self.class_prob_x_male_prob = self.class_prob_x_male_prob / sum(self.class_prob_x_male_prob)
        self.class_prob_x_female_prob = self.class_prob_x_female_prob / sum(self.class_prob_x_female_prob)

        # for ex 8  generate grades according to given std and mean
        HIF_mean, FIT_mean, HBGM_mean, HKUI_mean = 2.5, 3.0, 3.5, 4.0
        HIF_std, FIT_std, HBGM_std, HKUI_std = 1.2, 1.0, 0.5, 0.5
        MAX_GRADE = 5.0
        MIN_GRADE = 1.0
        low_high = lambda x_std, x_mean: ((MIN_GRADE - x_mean) / x_std, (MAX_GRADE - x_mean) / x_std)
        self.grade_prob_dist_per_class = {
            Departments.HIF: truncnorm.rvs(*low_high(HIF_std, HIF_mean), loc=HIF_mean, scale=HIF_std, size=10000),
            Departments.FIT: truncnorm.rvs(*low_high(FIT_std, FIT_mean), loc=FIT_mean, scale=FIT_std, size=10000),
            Departments.HBGM: truncnorm.rvs(*low_high(HBGM_std, HBGM_mean), loc=HBGM_mean, scale=HBGM_std, size=10000),
            Departments.HKUI: truncnorm.rvs(*low_high(HKUI_std, HKUI_mean), loc=HKUI_mean, scale=HKUI_std, size=10000),
        }

    def generate_record(self, idx: int | None = None) -> dict:
        id = idx  # 1)
        last_name = fake.last_name().upper()  # 2)
        gender = self._gender()  # 3)
        first_name = self._generate_first_name(gender=gender)  # 2nd2) ;)
        birthday = self._birthday()  # 4)
        class_1, birthday_adjusted_for_ex_7 = self._class1(gender=gender)  # 7)
        class_2 = self._class2()  # 7b)
        spg_id_c1 = self._spg_id(last_name=last_name, class_=class_1)  # 5)  class_1 as base for inscription year
        avg_grade = self._avg_grade(class_=class_2)  # 8)  (regex-Variante)

        return dict(
            **{'id': id} if id is not None else {},
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            birthday=birthday,
            class_1=class_1,
            birthday_adjusted_for_ex_7=birthday_adjusted_for_ex_7,
            class_2=class_2,
            spg_id_c1=spg_id_c1,
            avg_grade=avg_grade,

        )

    @staticmethod
    def _gender() -> str:
        return np.random.choice([g.value for g in Gender], p=[0.45, 0.45, 0.05, 0.02, 0.03])

    @staticmethod
    def _generate_first_name(
            gender: str
    ) -> str:
        match gender:
            case Gender.maennlich:
                return fake.first_name_male()
            case Gender.weiblich:
                return fake.first_name_female()
            case _:
                return fake.first_name()

    @staticmethod
    def _birthday() -> str:
        return fake.date_of_birth(minimum_age=14, maximum_age=20).strftime('%Y-%m-%d')

    def _class1(self, gender: str) -> tuple[str, str]:
        prob_dist = self.class_prob_x_male_prob
        if gender == Gender.weiblich:
            prob_dist = self.class_prob_x_female_prob
        class_ = np.random.choice(self.classes_info['Klasse'], p=prob_dist)
        grade = int(class_[0])
        min_realistic_age_for_gradde = 13 + grade
        birthday_adjusted_for_ex_7 = fake.date_of_birth(
            minimum_age=min_realistic_age_for_gradde, maximum_age=min_realistic_age_for_gradde + 1).strftime('%Y-%m-%d')
        return class_, birthday_adjusted_for_ex_7

    @staticmethod
    def _class2() -> str:
        return exrex.getone(rf'[1-5][A-C]({Departments.HIF}|{Departments.FIT}|{Departments.HBGM}|{Departments.HKUI})')

    @staticmethod
    def _spg_id(last_name: str, class_: str) -> str:
        CURRENT_YEAR = 23
        inscribtion_year = CURRENT_YEAR - int(class_[0])
        return f'{last_name[:3]}{inscribtion_year}{exrex.getone(r"[0-9]{4}")}'

    def _avg_grade(self, class_: str) -> float:
        dept = Departments(class_[2:])
        return np.random.choice(self.grade_prob_dist_per_class[dept])


def main():
    schuelerFaker = SchuelerListeRecordGenerator()
    headers = schuelerFaker.generate_record(0).keys()
    CSVExporter.export(
        schuelerFaker.records(n_records=10000),
        path=Path('../out', 'Wolf_4EHIF_MockSchueler01.csv'),
        headers=headers
    )


if __name__ == '__main__':
    main()
