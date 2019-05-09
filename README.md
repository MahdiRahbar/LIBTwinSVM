# LIBTwinSVM

## Core Features
LIBTwinSVM is an easy-to-use implementation of Twin Support Vector Machine.  It is licensed under the terms of GNU GPL v3. This application comes with a user interface which makes using the algorithm so handy for Data Scientists, Machine Learning Researchers and whoever else that is interested in Machine Learning.
<br>

- A **simple** and **user-friendly Graphical User Interface** (GUI).
- Supports both **standard TwinSVM** and **Least Squares TwinSVM** classifiers.
- Easy to import data in **CSV** & **LIBSVM** format.
- A dataset can be loaded with **shuffling** and **normalization**.
- A **fast optimizer** (clipDCD) is improved and implemented in C++ to solve optimization problems of TwinSVMs.
- Supports **Linear**, **RBF** and **Rectangular** kernel.
- Supports **Binary** and **Multi-class** classification (One-vs-All & One-vs-One).
- The OVA and OVO estimators are **compatible with scikit-learn** tools such as GridSearchCV, cross_val_score, etc.
- A classifier can be evaluated using either **K-fold cross-validation** or **Training/Test split**.
- Supports **grid search** over estimators' hyper-parameters.
- The detailed classification results can be saved in an **Excel-format spreadsheet** file.
- The classification results can be logged during the grid search process to not lose results in case of power failure.
- A **feature-rich visualization tool** to show decision boundaries and geometrical interpretation of TwinSVMs.
- The best-fitted classifier can be saved on the disk after the grid search process.



## Installation Guide
### Dependencies

LIBTwinSVM depends on the following packages.

|   Package                                      |                      Description                               |       License         |
| ---------------------------------------------- | -------------------------------------------------------------- | --------------------- |
| [Cython](https://cython.org/)                  |  To use C++ code in Python.                                    | Apache License 2.0    |
| [NumPy](https://www.numpy.org/)                |  Fast linear algebra operations.                               | BSD 3-Clause          | 
| [Matplotlib](https://matplotlib.org/)          |  Visualization and geometrical representation of classifiers.  | [Matplotlib License](https://matplotlib.org/users/license.html)                    |
| [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro)  | To create a GUI for using the LIBTwinSVM's features.| GPL |
| [Scikit-learn](https://scikit-learn.org/)      | For TwinSVM-based models evaluation and selection.             | BSD 3-Clause |
| [Pandas](https://pandas.pydata.org/)           | For reading and processing datasets.                           | BSD 3-Clause |
| [XlsxWriter](https://xlsxwriter.readthedocs.io/) | For saving classification results in an Excel file.          | BSD 3-Clause |
| [Joblib](https://xlsxwriter.readthedocs.io/)   | For saving and loading TwinSVM-based models.                   | BSD 3-Clause |
| [numpydoc](https://numpydoc.readthedocs.io/en/latest/) | API code documentation.                                | BSD License  |