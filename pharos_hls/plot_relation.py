import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.optimize import curve_fit
import numpy as np

def aggregate_df_by_mean(df, a, b):
    
    agg_table = (
        df.groupby(a)[b]
        .mean()
        .reset_index(name="mean")
        .rename(columns={a: "key"})
    )

    return agg_table.sort_values("key")

def plot_relation(df, hyperparam, hw_metric, func, hyperparam_name, metric_name, chart_name):

    agg = aggregate_df_by_mean(df, hyperparam, hw_metric)

    plt.figure(figsize=(8, 5))
    plt.plot(agg["key"], agg["mean"], marker="o")

    ax = plt.gca()

    if func is not None:
        func_params, _ = curve_fit(
            func,
            agg["key"],
            agg["mean"]
        )

        x_smooth = np.linspace(
            agg["key"].min(),
            agg["key"].max(),
            200
        )

        y_func = func(x_smooth, *func_params)
        ax.plot(x_smooth, y_func, linestyle="--")

    ax.xaxis.set_major_locator(ticker.MaxNLocator(
        integer=True,
        nbins=10  # máximo de ticks visíveis
    ))

    plt.xlabel(hyperparam_name)
    plt.ylabel(metric_name)

    plt.grid(True)

    if chart_name is not None:
        plt.savefig(chart_name)

    plt.show()