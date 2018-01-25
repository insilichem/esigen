# Local installation

If you need to process a lot of files or are worried about your privacy, we recommend using it locally.

1. Download and unzip [this repository](https://github.com/insilichem/esigen)
2. Download [Miniconda](https://conda.io/miniconda.html)
3. Create a new conda environment with one of the provided `environment*.yml` files and activate it
4. Run `esigenweb`

For Linux, this roughly translates to:

```
wget https://github.com/insilichem/esigen/archive/master.zip && unzip master.zip
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda*.sh
conda env create -f esigen-master/environment.yml # or environment-pymol.yml if you need CLI image rendering (not web)
conda activate esigen
esigenweb
```

The installation also provides an executable called `esigen` with the same purpose. Run `esigen -h` to print usage guidelines.