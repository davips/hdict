#  Copyright (c) 2021. Davi Pereira dos Santos
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

# library arff2pandas simply disappeared...
import re


def isplit(source, sep=None, regex=False):  # pragma: no cover
    """
    https://stackoverflow.com/a/9773142/9681577

    generator version of str.split()

    :param source:
        source string (unicode or bytes)

    :param sep:
        separator to split on.

    :param regex:
        if True, will treat sep as regular expression.

    :returns:
        generator yielding elements of string.
    """
    if sep is None:  # pragma: no cover
        # mimic default python behavior
        source = source.strip()
        sep = "\\s+"
        if isinstance(source, bytes):
            sep = sep.encode("ascii")
        regex = True
    if regex:
        # version using re.finditer()
        if not hasattr(sep, "finditer"):
            sep = re.compile(sep)
        start = 0
        for m in sep.finditer(source):
            idx = m.start()
            assert idx >= start
            yield source[start:idx]
            start = m.end()
        yield source[start:]
    else:
        # version using str.find(), less overhead than re.finditer()
        sepsize = len(sep)
        start = 0
        while True:
            idx = source.find(sep, start)
            if idx == -1:
                yield source[start:]
                return
            yield source[start:idx]
            start = idx + sepsize


def liac2pandas(arff):
    import pandas as pd

    attrs = arff["attributes"]
    attrs_t = []
    for attr in attrs:
        if isinstance(attr[1], list):
            attrs_t.append("%s@{%s}" % (attr[0], ",".join(attr[1])))
        else:
            attrs_t.append("%s@%s" % (attr[0], attr[1]))

    df = pd.DataFrame(data=arff["data"], columns=attrs_t)
    return df


def load(fp):
    import arff as liacarff

    data = liacarff.load(fp)
    return liac2pandas(data)


def loads(s):
    import arff as liacarff

    data = liacarff.loads(s)
    return liac2pandas(data)


def df2liac(df, relation="data", description=""):  # pragma: no cover
    attrs = []
    for col in df.columns:
        attr = col.split("@")
        if attr[1].count("{") > 0 and attr[1].count("}") > 0:
            vals = attr[1].replace("{", "").replace("}", "").split(",")
            attrs.append((attr[0], vals))
        else:
            attrs.append((attr[0], attr[1]))

    data = list(df.values)
    result = {"attributes": attrs, "data": data, "description": description, "relation": relation}
    return result


# def dump(df, fp):  # todo: : save arff/CSV from hdict
#     import arff as liacarff
#
#     arff = df2liac(df)
#     liacarff.dump(arff, fp)
#
#
# def dumps(df):  # todo: : output arff/CSV from hdict
#     import arff as liacarff
#
#     arff = df2liac(df)
#     return liacarff.dumps(arff)


def df2Xy(df, target=None):
    r"""
    >>> from hdict import hdict
    >>> from hdict.dataset.dataset import df2Xy
    >>> from testfixtures import TempDirectory
    >>> arff = "@RELATION mini\n@ATTRIBUTE attr1	REAL\n@ATTRIBUTE attr2 	REAL\n@ATTRIBUTE class 	{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1"
    >>> with TempDirectory() as tmp:  # doctest:+ELLIPSIS
    ...    tmp.write("mini.arff", arff.encode())
    ...    d = hdict.fromfile(tmp.path + "/mini.arff")
    '/tmp/.../mini.arff'
    >>> df2Xy(d.df)
    {'X':    attr1  attr2
    0    5.1    3.5
    1    3.1    4.5, 'y': array([0, 1])}
    >>> df2Xy(d.df, target="attr2")
    {'X':    attr1 class
    0    5.1     0
    1    3.1     1, 'y': 0    3.5
    1    4.5
    Name: attr2, dtype: float64}
    """
    if target is None:
        from sklearn.preprocessing import LabelEncoder

        le = LabelEncoder()
        X = df.drop(df.columns[[-1]], axis=1)
        y = le.fit_transform(df[df.columns[-1]])
    else:
        y = df[target]
        X = df.drop(target, axis=1)
    return {"X": X, "y": y}


def nom2bin(X, nomcols):
    """
    >>> import numpy as np
    >>> from pandas import DataFrame as DF
    >>> X = DF(np.array([[0, "a", 1.6], [3.2, "b", 2], [8, "c", 3]]))
    >>> X
         0  1    2
    0    0  a  1.6
    1  3.2  b    2
    2    8  c    3
    >>> nom2bin(X, nomcols=[1])
         0    2  1_a  1_b  1_c
    0    0  1.6    1    0    0
    1  3.2    2    0    1    0
    2    8    3    0    0    1
    """
    if X.__class__.__name__ in ["DataFrame", "Series"]:
        import pandas

        clabels = X.columns[nomcols]
        return pandas.get_dummies(X, prefix=clabels, columns=clabels, dtype=int)
    else:
        import numpy
        from sklearn.preprocessing import OneHotEncoder

        encoder = OneHotEncoder()
        nom = encoder.fit_transform(X.iloc[:, nomcols] if hasattr(X, "iloc") else X[:, nomcols]).toarray()
        num = numpy.delete(X, nomcols, axis=1).astype(float)
        return numpy.column_stack((nom, num))


#
#
# def df2arff(input="df", output="arff", **kwargs):
#     """
#     >>> from idict import let, idict
#     >>> d = idict.fromminiarff()
#     >>> d >>= let(df2arff, output="a")
#     >>> d.show(colored=False)
#     {
#         "a": "→(input output df)",
#         "_history": "idict---------arff2pandas-1.0.1--df2arff",
#         "df": "«{'attr1@REAL': {0: 5.1, 1: 3.1}, 'attr2@REAL': {0: 3.5, 1: 4.5}, 'class@{0,1}': {0: '0', 1: '1'}}»",
#         "_id": "Ojq9k7ZSbVjwLGlZ7uuqIyhoJPo.p36mAmav2Wul",
#         "_ids": {
#             "a": "wVPgESiPwobfFLLm591BKw6i2Zn.p36mAmav2Wul",
#             "_history": "D2NpAYrhyJW-.nOhh91ttSjrbGw.nZ8qxps9giws",
#             "df": "q3_b71eb05c4be05eba7b6ae5a9245d5dd70b81b (content: 6X_dc8ccea3b2e46f1c78967fae98b692701dc99)"
#         }
#     }
#     >>> d.a
#     '@RELATION data\\n\\n@ATTRIBUTE attr1 REAL\\n@ATTRIBUTE attr2 REAL\\n@ATTRIBUTE class {0, 1}\\n\\n@DATA\\n5.1,3.5,0\\n3.1,4.5,1\\n'
#     """
#     return {output: dumps(kwargs[input]), "_history": ...}
#
#
# def openml(Xout="X", yout="y", name="iris", version=1):
#     """
#     #>>> from idict import Ø
#     #>>> (Ø >> openml).show(colored=False)
#     #{
#         #"X": "→(Xout yout name version)",
#         #"y": "→(Xout yout name version)",
#         #"_history": "idict--------------sklearn-1.0.1--openml",
#         #"_id": "idict--------------sklearn-1.0.1--openml",
#         #"_ids": {
#             #"X": "KkSoAvgPmGq52PvPBqGFCEp9cSUCfb7eht9VpUdr",
#             #"y": "HOE9E-HnFYen6JNRC9cHgAamJlOWGYTPIVKvQu8W",
#             #"_history": "Efw0ebrPTxTiuJ.ZpVt-MvB62ja.kmrOYzrn-ljf"
#         #}
#     #}
#     #>>> (Ø >> openml).X.head()
#        #sepallength  sepalwidth  petallength  petalwidth
#     #0          5.1         3.5          1.4         0.2
#     #1          4.9         3.0          1.4         0.2
#     #2          4.7         3.2          1.3         0.2
#     #3          4.6         3.1          1.5         0.2
#     #4          5.0         3.6          1.4         0.2
#     #>>> (Ø >> openml).y.head()
#     #0    Iris-setosa
#     #1    Iris-setosa
#     #2    Iris-setosa
#     #3    Iris-setosa
#     #4    Iris-setosa
#     #Name: class, dtype: category
#     #Categories (3, object): ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
#     """
#     from sklearn.datasets import fetch_openml
#
#     X, y = fetch_openml(name=name, version=version, as_frame=True, return_X_y=True)
#     return {Xout: X, yout: y, "_history": ...}
#
#
