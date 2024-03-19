
# Installation on Levante

Levante is the current (year 2024) supercomputer at DKRZ (German Climate Computing Center). 

Two steps are needed to get SynsatiPy running on "standard" datasets. First, the forward operator RTTOV needs to be installed and second the python package SynSatiPy also needs a separate installation.

## Step I: Installation of RTTOV

## Step II: Installation of SynSatiPy


**(i) Setting up a virtual python env**

```bash
cd /work/bb1262/tools/conda
python -m venv python3.10_synsatipy
source python3.10_synsatipy/bin/activate
```


**(ii) Get SynSatiPy and install it**

```bash
# git clone ...

# install in dev mode
pip install -e .
```

**(iii) prepare environment**

```bash
export RTTOV_PYTHON_WRAPPER=/work/bb1262/tools/rttov/rttov-v13.2/wrapper/
ulimit -s 204800
```

**(iv) run tests**
```bash
pip install pytest

cd synsatipy
pytest
```
If all tests run successfully than the installation procedure went well up to this point.


## Step III: Setting up a Dedicated Jupyter Kernel

This is a bit tricky because we need to use python from our env, but jupyter from the base conda.

**(i) clean up everything**
```bash
module purge
deactivate
```

**(ii) load envs in the correct order**
```bash
module load python3
source /work/bb1262/tools/conda/python3.10_synsatipy/bin/activate
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

source /work/bb1262/tools/conda/python3.10_synsatipy/bin/activate

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



