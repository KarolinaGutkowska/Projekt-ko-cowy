# This is a sample Python script.

from HUBA.huba import HUBA

huba = HUBA()

clean_file, report = huba.run(
    input_file="dane.xlsx",
    output_file="dane_clean.xlsx"
)