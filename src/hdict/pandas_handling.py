#  Copyright (c) 2023. Davi Pereira dos Santos
#  This file is part of the hdict project.
#  Please respect the license - more about this in the section (*) below.
#
#  hdict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  hdict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with hdict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#

from hdict.content.value import value


def explode_df(df) -> value:
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
