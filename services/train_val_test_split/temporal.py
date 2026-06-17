import argparse

import pandas as pd
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parent.parent
DEFAULT_CLEAN_PATH = ROOT / 'data' / 'clean.parquet'
DEFAULT_OUT_DIR = ROOT / 'data' / 'split' / 'temporal'
DEFAULT_TRAIN_END = 20
DEFAULT_VAL_END = 25


def temporal_split(
        clean_df_path: Path = DEFAULT_CLEAN_PATH,
        out_dir: Path = DEFAULT_OUT_DIR,
        train_end: int = DEFAULT_TRAIN_END,
        val_end: int = DEFAULT_VAL_END
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    clean_df = pd.read_parquet(clean_df_path)

    train_df = clean_df[clean_df['day'] < train_end]
    val_df = clean_df[(clean_df['day'] >= train_end) & (clean_df['day'] < val_end)]
    test_df = clean_df[clean_df['day'] >= val_end]

    out_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_parquet(out_dir / 'train.parquet')
    val_df.to_parquet(out_dir / 'val.parquet')
    test_df.to_parquet(out_dir / 'test.parquet')

    return train_df, val_df, test_df


def main():
    parser = argparse.ArgumentParser(description='Make train/val/test split from clean data.')
    parser.add_argument('--clean-df-path', type=Path, default=DEFAULT_CLEAN_PATH)
    parser.add_argument('--out-dir', type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument('--train-end', type=int, default=DEFAULT_TRAIN_END)
    parser.add_argument('--val-end', type=int, default=DEFAULT_VAL_END)
    args = parser.parse_args()

    temporal_split(
        clean_df_path=args.clean_df_path,
        out_dir=args.out_dir,
        train_end=args.train_end,
        val_end=args.val_end,
    )


if __name__ == '__main__':
    main()
