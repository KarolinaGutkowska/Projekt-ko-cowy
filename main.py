from HUBA.huba import HUBA


def main():
    huba = HUBA()

    df = huba.load_data("dane.csv")

    print(df.head())
    print(huba.report)


if __name__ == "__main__":
    main()