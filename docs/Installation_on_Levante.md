
# Installation on Levante

Levante is the current (year 2024) supercomputer at DKRZ (German Climate Computing Center). 

Three steps are needed to get SynsatiPy running on "standard" datasets.
- First, the package source of SynSatiPy needs to be downloaded
- Second, the forward operator RTTOV needs to be installed and 
- third the python package SynSatiPy also needs a separate installation.

It is assumed that all different activities happen a meaningfully chosen place, e.g. `~/tools`. If you need to prepared it , do

```bash
mkdir ~/tools   # or any other place your directory structure
cd ~/tools
```


## Step I: Download SynSatiPy Package 
The SynSatiPy package is downloaded from github.com first for two reasons:
1. we will use specific configuration files prepared for the installation of RTTOV version x. 
2. we will install the python installation after RTTOV installation from the downloaded source


**(i) download sources from github.com**
```bash 
git clone https://github.com/fsenf/SynSatiPy.git
```

**(ii) remember where configuration is stored**

Check which configuration files are available
```bash
ls -l SynSatiPy/config/rttov*
```

The RTTOV version-specific subdirectory, e.g. `SynSatiPy//config/rttov-v13` is used as `<PATH2CONFIG>` in the following. 

## Step II: Installation of RTTOV

After you downloaded and untared the RTTOV source code (assume the place is `~/tools/rttov`):

**(i) link in the correct Makefile**
```bash
cd build
mv Makefile.local Makefile.local~
cp <PATH2CONFIG>/Makefile.levante.ifort .
ln -s Makefile.levante.ifort Makefile.local
```

**(ii) setup the correct architecture**
```bash
cp <PATH2CONFIG>/ifort-openmp-levante arch/
```

**(iii) prepare compilation**

```bash
module purge

#--- check that no conda env is loaded
# source ~/.bash_condainit
# conda deactivate

module load intel-oneapi-compilers openmpi/4.1.2-intel-2021.5.0 
module load python3

cd ../src
../build/Makefile.PL RTTOV_NETCDF=1 RTTOV_F2PY=1 RTTOV_USER_LAPACK=0
```


**(iv) run compilation**
```bash
make ARCH=ifort-openmp-levante -j 8
```

**(iv) additional data**

*see RTTOV documentation*


## Step III: Installation of SynSatiPy


**(i) Setting up a virtual python env**

go to your place where python/conda envs are stored

```bash
cd ~/tools
mkdir python
cd python

python -m venv python3.10_synsatipy
source python3.10_synsatipy/bin/activate
```


**(ii) Go to SynSatiPy and install it**

```bash
cd ~/tools/SynSatiPy   # or where you actually did the clone for step I

# install in dev mode
pip install -e .
```

**(iii) prepare environment**

```bash
export RTTOV_PYTHON_WRAPPER=$HOME/tools/rttov/wrapper/
ulimit -s 204800
```

**(iv) run tests**
```bash
pip install pytest

cd synsatipy
pytest
```
If all tests run successfully than the installation procedure went well up to this point.


## Step IV: Setting up a Dedicated Jupyter Kernel

This is a bit tricky because we need to use python from our env, but jupyter from the base conda.

**(i) clean up everything**
```bash
module purge
deactivate
```

**(ii) load envs in the correct order**
```bash
module load python3
source $HOME/tools/python/python3.10_synsatipy/bin/activate
```

**(iii) create a jupyter kernel with standard methods**
```bash
pip install ipykernel
python -m ipykernel install --user --name python3-synsatipy  --display-name="SynSatiPy (Python 3.10)"
```

**(iv) update kernel config**
```bash
# go to the place where the kernel is defined, e.g.
cd ~/.local/share/jupyter/kernels/python3-synsatipy
```

 *you need to have a starter there like*
```bash
> cat start-kernel.sh 
#!/bin/bash

source /etc/profile
source ~/.bashrc

source $HOME/tools/python/python3.10_synsatipy/bin/activate

ulimit -s 204800
python -m ipykernel_launcher -f "$1"
```

*and an updated kernel file like*
```bash
> cat kernel.json
{
 "argv": [
  "/home/b/b380352/.local/share/jupyter/kernels/python3.10_synsatipy/start-kernel.sh",
  "{connection_file}"
 ],
 "display_name": "SynSatiPy (Python 3.10)",
 "language": "python",
 "metadata": {
  "debugger": true
 }
}

```



