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


def explode_df(df):
    """
    >>> from pandas import DataFrame
    >>> from hdict import hdict, cache
    >>> df = DataFrame({"x": [1,2,3], "y": [5,6,7]}, index=["a", "b", "c"])
    >>> d = hdict(df_=df)
    >>> d.show(colored=False)
    {
        df_: "‹{'x': {'a': 1, 'b': 2, 'c': 3}, 'y': {'a': 5, 'b': 6, 'c': 7}}›",
        df: {
            index: "‹{'a': 'a', 'b': 'b', 'c': 'c'}›",
            x: "‹{'a': 1, 'b': 2, 'c': 3}›",
            y: "‹{'a': 5, 'b': 6, 'c': 7}›",
            _id: efFl2-CCjnStQSpp8QmwkK-7ANKh8bNctOap9X9m,
            _ids: {
                index: HdOKL6NHC9ApFmGygZ54A9f265R6TxhGjBRwdO9r,
                x: n7fkFYWuvJ.MTp7asUu8489mQMwoZiL.5.or1EDt,
                y: N9Of5idOlZFH25hFb9IcjOwJrxt2.tXddWKuYq94
            }
        },
        _id: symsSXy-oMJrIpAisV7aHbn.fZ9yfjfrExxIq6HS,
        _ids: {
            df: efFl2-CCjnStQSpp8QmwkK-7ANKh8bNctOap9X9m,
            df_: e.VIUfoRxV4B6aoIZeJ8AlDwmq7IZNPDNPFI72WZ
        }
    }
    >>> d.df_
       x  y
    a  1  5
    b  2  6
    c  3  7
    >>> c = {}
    >>> d >>= cache(c)
    >>> d.show(colored=False)
    {
        df_: "‹{'x': {'a': 1, 'b': 2, 'c': 3}, 'y': {'a': 5, 'b': 6, 'c': 7}}›",
        df: {
            index: "‹{'a': 'a', 'b': 'b', 'c': 'c'}›",
            x: "‹{'a': 1, 'b': 2, 'c': 3}›",
            y: "‹{'a': 5, 'b': 6, 'c': 7}›",
            _id: efFl2-CCjnStQSpp8QmwkK-7ANKh8bNctOap9X9m,
            _ids: {
                index: HdOKL6NHC9ApFmGygZ54A9f265R6TxhGjBRwdO9r,
                x: n7fkFYWuvJ.MTp7asUu8489mQMwoZiL.5.or1EDt,
                y: N9Of5idOlZFH25hFb9IcjOwJrxt2.tXddWKuYq94
            }
        },
        _id: symsSXy-oMJrIpAisV7aHbn.fZ9yfjfrExxIq6HS,
        _ids: {
            df: efFl2-CCjnStQSpp8QmwkK-7ANKh8bNctOap9X9m,
            df_: e.VIUfoRxV4B6aoIZeJ8AlDwmq7IZNPDNPFI72WZ
        }
    }
    >>> d.df.show(colored=False)
    {
        index: "‹{'a': 'a', 'b': 'b', 'c': 'c'}›",
        x: "‹{'a': 1, 'b': 2, 'c': 3}›",
        y: "‹{'a': 5, 'b': 6, 'c': 7}›",
        _id: efFl2-CCjnStQSpp8QmwkK-7ANKh8bNctOap9X9m,
        _ids: {
            index: HdOKL6NHC9ApFmGygZ54A9f265R6TxhGjBRwdO9r,
            x: n7fkFYWuvJ.MTp7asUu8489mQMwoZiL.5.or1EDt,
            y: N9Of5idOlZFH25hFb9IcjOwJrxt2.tXddWKuYq94
        }
    }
    """
    from hdict.data.frozenhdict import frozenhdict

    dic = {"index": df.index.to_series()}
    for col in df:
        dic[str(col)] = df[col]
    d = frozenhdict(dic)
    return d


def file2df(filename, hide_types=True, return_name=True, transpose=False, index=False):
    from hdict.dataset.dataset import load

    if filename.endswith(".arff"):
        relation = None
        with open(filename) as f:
            for line in f:
                if line[:9].upper() == "@RELATION":
                    relation = line[9:-1]
                    break
        with open(filename) as f:
            df = load(f)

        if index or transpose:
            indexname = df.columns[0]
            df.set_index(indexname, inplace=True)
            df.index.name = indexname
        if transpose:
            df = df.T
            if index:
                df.index.rename(indexname, inplace=True)

        if hide_types:
            df.rename(columns={k: k.split("@")[0] for k in df.columns}, inplace=True)
        if return_name:
            return df, relation or filename
        else:
            return df
    elif filename.endswith(".csv"):
        from pandas import read_csv

        df = read_csv(filename)

        if index or transpose:
            indexname = df.columns[0]
            df.set_index(indexname, inplace=True)
            df.index.name = indexname
        if transpose:
            df = df.T
            if index:
                df.index.rename(indexname, inplace=True)

        if return_name:
            return df, filename
        else:
            return df
    else:  # pragma: no cover
        raise Exception(f"Unknown extension {filename.split('.')[-1]}.")
