import argparse
from pathlib import Path
from kmz_maker.build import build_kmz

def main():
    ap = argparse.ArgumentParser(description="Build a KMZ from a CSV of points/trails.")
    ap.add_argument("--csv", required=True, help="Input CSV path")
    ap.add_argument("--out", required=True, help="Output KMZ path")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    kmz_path = build_kmz(args.csv, str(out))
    print(f"Saved: {kmz_path}")

if __name__ == "__main__":
    main()
