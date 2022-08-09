from pathlib import Path
import numpy as np
import pandas as pd
import requests
import tenacity
from datetime import datetime
from typing import Optional, Union


def ensure_dataset_exists(id:str, dest_path: Path, force: bool = False):
    """Downloads a file from Google Drive to local storage.
    
    Arguments:
        id: GDrive file id
        dest_path: File destination in local storage 
        force: Whether to force the download or not
    """
    @tenacity.retry(stop=tenacity.stop_after_attempt(7))
    def get_raw_content(id:str):
        url = f'https://drive.google.com/uc?id={id}&export=download&confirm=t'
        response = requests.get(url)
        response.raise_for_status()
        return response

    if not dest_path.exists() or force:
        response = get_raw_content(id)
        raw_content = response.content
        dest_path.parent.mkdir(exist_ok=True, parents=True)
        with open(str(dest_path), 'w') as file:
            file.write(raw_content.decode())

        print(f"File successfully saved in {dest_path}")
    
    else:
        print(f"File {dest_path} exists!")


def load_loan_funding_info(filepath: Union[str, Path]) -> pd.DataFrame:
    """Loads and returns `loan_funding_origination_info.csv`"""
    df = pd.read_csv(filepath, parse_dates=["OriginationDate"])
    
    return df


def load_dindex_dataset(filepath: Union[str, Path]) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    return df

def load_loan_paymets(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Loads and returns `loan_payments_dataset.csv`
    """
    df = pd.read_csv(
        filepath, 
        parse_dates=["PaymentDueDate", "PaymentTransferDate", "PaymentProcessingDate"]
    )

    return df



def load_loan_payments_dataset_scoring(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Loads and returns a sanitized version of `loan_payments_dataset_scoring.csv`
    """
    def _get_payment_date_from_payment_code(code: str) -> datetime:
        year = int("20" + code[2:4])
        month = int(code[4:6])
        day = int(code[6:8])
        return datetime(year, month, day)

    def _get_payment_source_from_id(pid: int) -> str:
        if pid == 0:
            return "Regular"
        elif pid == 1:
            return "Alternative"
        elif pid == 2:
            return "Contractor"
        
        if pid in [4, 8, 13]:
            return "Additional"
        
        raise Exception(f"Unmapped PaymentTypeId: {pid}")
    
    def _get_payment_type_from_id(pid: int) -> Optional[int]:
        if pid in [0, 1, 2]:
            return None
        
        return pid

    def _get_payment_type_description_from_id(pid: int) -> Optional[str]:
        if pid in [0, 1, 2]:
            return None

        if pid == 4:
            return "Prepayment"
        
        if pid in [8, 13]:
            return "Restructuring"
        
        raise Exception(f"Unmapped PaymentTypeId: {pid}")


    df = pd.read_csv(
        filepath, 
        header=None,
        names=["PaymentCode", "PaymentPrincipal"],
        usecols=[0, 1],
        dtype=str
    )

    df["PaymentTypeId"] = df["PaymentCode"].apply(lambda code: code[0:2])
    df["PaymentTypeId"] = df["PaymentTypeId"].astype(int)

    df["PaymentSource"] = df["PaymentTypeId"].apply(_get_payment_source_from_id)
    df["PaymentType"] = df["PaymentTypeId"].apply(_get_payment_type_from_id)
    df["PaymentTypeDescription"] = df["PaymentTypeId"].apply(_get_payment_type_description_from_id)

    df["PaymentProcessingDate"] = df["PaymentCode"].apply(_get_payment_date_from_payment_code)
    df["LoanId"] = df["PaymentCode"].apply(lambda code: code[8:])
    df["LoanId"] = df["LoanId"].astype(int)

    df = df.drop(["PaymentTypeId"], axis=1)

    df = df.fillna(value=np.nan)

    df = df[["LoanId", "PaymentSource", "PaymentType", "PaymentTypeDescription", "PaymentPrincipal", "PaymentProcessingDate", "PaymentCode"]]

    return df


def load_loan_agencies(filepath: Union[str, Path], just_naboo: bool = False) -> pd.DataFrame:
    """
    Loads and returns loan agencies from Naboo
    """
    df = pd.read_csv(filepath)

    if just_naboo:
        return df.loc[df.Country == "Naboo"]

    return df
