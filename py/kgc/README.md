Gui features included:
* re-centering (click on point to re-centre)
* band-switching (assign 3-d coordinates: e.g. r0<return>, g1<return>, b1<return> to assign first three bands to x, y, z for the 3d vis

### Notes
* Code samples tested on Mac and Linux so far, should be windows compatible
* [please click here to see slides](presentation.pdf)

## Setup
setup.sh contains dependency install line

## Running the codes at a terminal:
```
python3 kgc.py [input csv file] [number of K-nearest neighbours (defaults to math.ceil(math.sqrt(N))]
# where N is the number of data points]

python3 view.py [output csv file from kgc.py]
```

## Instructions to run the examples:
rm *.p  # remove any stray "pickle" files (distance matrix gets cached)

### 0
```
python3 kgc.py example_00_simple.csv
python3 view.py example_00_simple.csv_output.csv
```
### 1
```
python3 kgc.py example_01_bimodal.csv
python3 view.py example_01_bimodal.csv_output.csv
```
### 2
```
python3 kgc.py example_02_iris.csv
python3 view.py example_02_iris.csv_output.csv
```

### 3
```
python3 kgc.py example_03_bear.csv 1000
python3 view.py example_03_bear.csv_output.csv
```

## References
[1] [Unsupervised Nonparametric Classification of Polarimetric SAR Data Using The K-nearest Neighbor Graph, A. Richardson et al, proc. IEEE IGARSS, Honolulu, Hawaii, July 2010](https://ieeexplore.ieee.org/document/5651992)

[2] [Hierarchical Unsupervised Nonparametric Classification of Polarimetric SAR Time Series Data, A. Richardson et al, proc. IEEE IGARSS, Québec City, Canada, July 2014](https://ieeexplore.ieee.org/document/6947550)

