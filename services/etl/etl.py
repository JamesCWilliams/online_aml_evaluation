import argparse

import pandas as pd
import numpy as np
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parent.parent
DEFAULT_TX_LOG_PATH = ROOT / 'data' / 'tx_log.csv'
DEFAULT_ACCOUNTS_PATH = ROOT / 'data' / 'accounts.csv'
DEFAULT_SAR_ACCOUNTS_PATH = ROOT / 'data' / 'sar_accounts.csv'
DEFAULT_OUT_PATH = ROOT / 'data' / 'clean.parquet'
DEFAULT_DROP_LIST = [
    'type',
    'orig_type',
    'dest_type',
    'orig_acct_stat',
    'dest_acct_stat',
    'orig_acct_rptng_crncy',
    'dest_acct_rptng_crncy',
    'orig_bank_id',
    'dest_bank_id',
    'orig_country',
    'dest_country',
    'orig_tx_behavior_id',
    'dest_tx_behavior_id',
    'orig_close_dt',
    'dest_close_dt',
    'alertID',
    'ALERT_ID',
    'orig_dsply_nm',
    'dest_dsply_nm',
    'orig_ssn',
    'dest_ssn',
    'orig_first_name',
    'orig_last_name',
    'dest_first_name',
    'dest_last_name',
    'orig_street_addr',
    'dest_street_addr',
    'orig_zip',
    'dest_zip',
    'orig_lat',
    'dest_lat',
    'orig_lon',
    'dest_lon',
    'orig_gender',
    'dest_gender',
    'ALERT_TYPE',
    'orig_branch_id',
    'dest_branch_id',
    'orig_open_dt',
    'dest_open_dt',
    'orig_city',
    'dest_city',
    'orig_state',
    'dest_state',
    'orig_birth_date',
    'dest_birth_date',
    'orig_acct_id',
    'dest_acct_id',
    # raw values superseded by engineered features
    'oldbalanceOrig',
    'newbalanceOrig',
    'oldbalanceDest',
    'newbalanceDest',
    'amount',
    'step',
    # identifiers not useful for modeling
    'nameOrig',
    'nameDest',
]
SOURCE_FEATURES = [
    'amount',
    'step',
    'oldbalanceOrig',
    'newbalanceOrig',
    'newbalanceDest',
    'oldbalanceDest',
    'orig_initial_deposit',
    'dest_initial_deposit',
    'nameOrig',
    'nameDest',
    'orig_prior_sar_count',
    'dest_prior_sar_count',
    ]


def merge_sources(
        tx_log_path: Path = DEFAULT_TX_LOG_PATH,
        accounts_path: Path = DEFAULT_ACCOUNTS_PATH,
        sar_accounts_path: Path = DEFAULT_SAR_ACCOUNTS_PATH
) -> pd.DataFrame:
    """

    """
    tx_log_df = pd.read_csv(tx_log_path)
    accounts_df = pd.read_csv(accounts_path)
    sar_accounts_df = pd.read_csv(sar_accounts_path)

    merged_df = tx_log_df.merge(
        accounts_df.add_prefix('orig_'),
        left_on='nameOrig',
        right_on='orig_acct_id',
        how='left'
    )

    merged_df = merged_df.merge(
        accounts_df.add_prefix('dest_'),
        left_on='nameDest',
        right_on='dest_acct_id',
        how='left'
    )
    
    alert_meta = sar_accounts_df[['ALERT_ID', 'ALERT_TYPE']].drop_duplicates('ALERT_ID')

    merged_df = merged_df.merge(
        alert_meta,
        left_on='alertID',
        right_on='ALERT_ID',
        how='left'
    )

    merged_df['ALERT_TYPE'] = merged_df['ALERT_TYPE'].fillna('none')

    return merged_df


def drop_columns(
        df: pd.DataFrame,
        drop_list: list[str] = DEFAULT_DROP_LIST
) -> pd.DataFrame:
    """

    """
    if not set(drop_list).issubset(set(df.columns.to_list())):
        raise Exception(
            f'drop list contains columns not found in the df columns!\ndrop list: {drop_list}\ndf columns: {df.columns}'
            )
    
    return df.drop(columns=drop_list)


def compute_features(
        df: pd.DataFrame
) -> pd.DataFrame:
    """

    """
    if not set(SOURCE_FEATURES).issubset(set(df.columns.to_list())):
        raise Exception(
            f'all required columns are not present in df!\nrequired: {SOURCE_FEATURES}\ndf columns: {df.columns}'
            )
    
    # non-temporal features
    df['log_amount'] = np.log1p(df['amount'])
    df['hour_of_day'] = df['step'] % 24
    df['day'] = df['step'] // 24
    df['log_orig_balance_error'] = np.log1p((df['oldbalanceOrig'] - df['newbalanceOrig'] - df['amount']).abs())
    df['log_dest_balance_error'] = np.log1p((df['newbalanceDest'] - df['oldbalanceDest'] - df['amount']).abs())
    df['orig_sent_fraction'] = df['amount'] / (df['oldbalanceOrig'] + 1)
    df['log_dest_recv_fraction'] = np.log1p(df['amount'] / (df['oldbalanceDest'] + 1))
    df['near_10k'] = ((df['amount'] >= 9_000) & (df['amount'] < 10_000)).astype(int)
    df['amount_vs_orig_deposit'] = df['amount'] / (df['orig_initial_deposit'] + 1)
    df['amount_vs_dest_deposit'] = df['amount'] / (df['dest_initial_deposit'] + 1)

    # temporal features; sort by time!
    df = df.sort_values('step').reset_index(drop=True)
    df['log_orig_tx_count'] = np.log1p(df.groupby('nameOrig').cumcount())
    df['log_orig_total_sent'] = np.log1p(df.groupby('nameOrig')['amount'].cumsum() - df['amount'])
    df['orig_avg_sent'] = df['log_orig_total_sent'] / (df['log_orig_tx_count'] + 1)
    df['log_dest_tx_count'] = np.log1p(df.groupby('nameDest').cumcount())
    df['log_dest_total_recv'] = np.log1p(df.groupby('nameDest')['amount'].cumsum() - df['amount'])
    df['dest_avg_recv'] = df['log_dest_total_recv'] / (df['log_dest_tx_count'] + 1)
    df['_is_new_pair'] = (~df.duplicated(subset=['nameOrig', 'nameDest'], keep='first')).astype(int)
    df['log_dest_unique_senders'] = np.log1p(df.groupby('nameDest')['_is_new_pair'].cumsum() - df['_is_new_pair'])
    df['log_orig_unique_recipients'] = np.log1p(df.groupby('nameOrig')['_is_new_pair'].cumsum() - df['_is_new_pair'])
    df['orig_prior_sar_count'] = df['orig_prior_sar_count'].astype(int)
    df['dest_prior_sar_count'] = df['dest_prior_sar_count'].astype(int)

    df.drop(columns=['_is_new_pair'], inplace=True)

    return df


def etl(
        tx_log_path: Path = DEFAULT_TX_LOG_PATH,
        accounts_path: Path = DEFAULT_ACCOUNTS_PATH,
        sar_accounts_path: Path = DEFAULT_SAR_ACCOUNTS_PATH,
        drop_list: list[str] = DEFAULT_DROP_LIST,
        out_path: Path = DEFAULT_OUT_PATH
) -> pd.DataFrame:

    df = merge_sources(tx_log_path, accounts_path, sar_accounts_path)
    df = compute_features(df)
    df = drop_columns(df, drop_list)

    df.to_parquet(out_path)

    return df


def main():
    parser = argparse.ArgumentParser(description='Run the AML ETL pipeline.')
    parser.add_argument('--tx-log-path', type=Path, default=DEFAULT_TX_LOG_PATH)
    parser.add_argument('--accounts-path', type=Path, default=DEFAULT_ACCOUNTS_PATH)
    parser.add_argument('--sar-accounts-path', type=Path, default=DEFAULT_SAR_ACCOUNTS_PATH)
    parser.add_argument('--out-path', type=Path, default=DEFAULT_OUT_PATH)
    args = parser.parse_args()

    etl(
        tx_log_path=args.tx_log_path,
        accounts_path=args.accounts_path,
        sar_accounts_path=args.sar_accounts_path,
        out_path=args.out_path,
    )


if __name__ == '__main__':
    main()
