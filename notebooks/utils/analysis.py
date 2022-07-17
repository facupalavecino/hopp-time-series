import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.figure import Figure


def nan_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame with the NaN ratio of each column in `df`
    
    Arguments:
        df: DataFrame to analyze

    Returns:
        DataFrame with the NaN ratio of each column
    """
    ratios = []

    length = len(df)

    for column in df.columns.values:
        ratios.append(
            pd.Series(
                data=len(df.loc[df[column].isna()]) / length,
                name=column
            )
        )

    return pd.DataFrame(data=ratios).rename(columns={0: "nan_ratio"})

def histogram_and_boxplot(s: pd.Series) -> Figure:
    """Returns a Figure with 2 plots: an histogram and a boxplot of the series"""

    fig, ax = plt.subplots(
        nrows=2,
        ncols=1,
        sharex=True,
        **{"figsize": (8, 5), "dpi": 125, "facecolor": "white"},
    )

    ax[0].set_title(f"Distribution of InstallmentAmount")

    ax[0].hist(
        x=s,
        color="steelblue",
        alpha=0.7,
        label="InstallmentAmount"
    )

    ax[0].set_xlabel("Amount [$]")
    ax[0].set_ylabel("Frequency")
    ax[0].legend()
    ax[0].grid(alpha=0.25)

    ax[1].boxplot(s, showmeans=True, meanline=True, vert=False)
    ax[1].set_xlabel("Amount [$]")

    plt.tight_layout()
    plt.show()

    return fig
