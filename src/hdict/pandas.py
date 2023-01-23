

def explode_df(df):
    """
    >>> from pandas import DataFrame
    >>> from hdict import hdict
    >>> df = DataFrame({"x": [1,2,3], "y": [5,6,7]}, index=["a", "b", "c"])
    >>> d = hdict(df=df)
    >>> d.show(colored=False)
    {
        df: "«{'x': {'a': 1, 'b': 2, 'c': 3}, 'y': {'a': 5, 'b': 6, 'c': 7}}»",
        df_: {
            index: "«{'a': 'a', 'b': 'b', 'c': 'c'}»",
            x: "«{'a': 1, 'b': 2, 'c': 3}»",
            y: "«{'a': 5, 'b': 6, 'c': 7}»",
            _id: "CO3m4w1vqM.etZXkoHQoNxA.PS.kQI-LomW.H6VC",
            _ids: {
                index: "HBNoEs58wCDhsdWWisp0sjMwsWmNMXuwaGFE9UAt",
                x: "3F.7UkfLr2tpB-FxATaRJYIpbYpg9oa1r5M31M0j",
                y: "bqYjHGDn-brebdANtxtNo4OkpOXfDwwVYejlzo4t"
            }
        },
        _id: "qMP.-f8p3zIrmTuOOqBLCVurT6uIIfihnR3rZne4",
        _ids: {
            df: "CO3m4w1vqM.etZXkoHQoNxA.PS.kQI-LomW.H6VC"
        }
    }
    >>> d.df
       x  y
    a  1  5
    b  2  6
    c  3  7
    """
    from hdict.frozenhdict import frozenhdict
    from hdict import value

    dic = {"index": df.index.to_series()}
    for col in df:
        dic[str(col)] = df[col]
    d = frozenhdict(dic)
    return value(df, d.hosh, hdict=d)
