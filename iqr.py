import pandas as pd
import numpy as np

# IN  = "tpch_timings_us.csv"                 # 22 x 100, índice=Q1..Q22
# OUT = "tpch_timings_us_no_outliers.csv"

# def remove_outliers_iqr_row(s: pd.Series, k: float = 1.5) -> pd.Series:
#     s = pd.to_numeric(s, errors="coerce")
#     q1, q3 = s.quantile(0.25), s.quantile(0.75)
#     iqr = q3 - q1
#     lo, hi = q1 - k*iqr, q3 + k*iqr
#     return s.where((s >= lo) & (s <= hi))  # outliers -> NaN

# df = pd.read_csv(IN, index_col=0)
# filtered = df.apply(remove_outliers_iqr_row, axis=1)

# # opcional: manter inteiros com células vazias
# filtered = filtered.round().astype("Int64")  # requer pandas >= 1.0
# filtered.to_csv(OUT, na_rep="")


CSV_IN = "tpch_timings_us.csv"           # 22 x 100 (index=Q1..Q22, cols=0..99)
CSV_OUT_MEANS = "means_equalized.csv"   

def remove_outliers_iqr(row: pd.Series, k: float = 1.5) -> pd.Series:
    s = pd.to_numeric(row, errors="coerce")              # garante numérico
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - k*iqr, q3 + k*iqr
    keep = (s >= lo) & (s <= hi)
    return s[keep].dropna()                              # mantém ordem original

def main():
    df = pd.read_csv(CSV_IN, index_col=0)

    # remove outliers por linha
    filtered = {idx: remove_outliers_iqr(row) for idx, row in df.iterrows()}

    #  acha n_min
    lengths = {idx: len(s) for idx, s in filtered.items()}
    min_row, n_min = min(lengths.items(), key=lambda x: x[1])

    if n_min == 0:
        raise ValueError("Após remoção de outliers, alguma linha ficou sem observações (n_min=0).")

    print(f"Linha limitante: {min_row} com n_min={n_min}")

    # = médias usando = n_min valores por linha
    means = {}
    for idx, s in filtered.items():
        means[idx] = float(s.sample(n=n_min, random_state=0).mean())

    means_ser = pd.Series(means, name="mean_us").sort_index()
    print(means_ser)

    # opcional: salvar
    out = pd.DataFrame({"mean_us": means_ser, "n_used": n_min})
    out.to_csv(CSV_OUT_MEANS)

if __name__ == "__main__":
    main()
