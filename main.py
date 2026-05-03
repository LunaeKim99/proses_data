import os
from modules.data_loader import load_data
from modules.feature_engineer import engineer_features
from modules.exporter import export_csvs
from modules.visualizer import generate_charts

OUTPUT_DIR = "output"
DATA_PATH = "dataset.csv"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("📂 Output folder ready.\n")

    print("📥 Loading dataset...")
    df = load_data(DATA_PATH)
    print(f"   → {len(df)} provinces loaded.\n")

    print("⚙️  Engineering features...")
    df = engineer_features(df)
    print("   → Features added.\n")

    print("💾 Exporting CSV files...")
    export_csvs(df, OUTPUT_DIR)
    print()

    print("📊 Generating charts...")
    generate_charts(df, OUTPUT_DIR)
    print()

    print("✅ All done! Check the 'output/' folder.")

if __name__ == "__main__":
    main()
