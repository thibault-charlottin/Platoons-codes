# ADAS vs HDV impact on platoons
This reposit contains code to detect platoons in the TGSIM I294 L1 dataset as presented in the article "Identifying platoons in traffic: Towards an assessment of ACC
platoon impacts". Data can be downloaded at https://data.transportation.gov/Automobiles/Third-Generation-Simulation-Data-TGSIM-I-294-L1-Tr/7zjf-a4zf/about_data . <br>


## File structure

```
📦Mother folder
 ┣ 📂conda
 ┃ ┗ 📜env.yaml
 ┣ 📂data #folder to be created to insert TGSIM L1 dataset in it
 ┣ 📂src
 ┃ ┣ 📂DTW
 ┃ ┣ 📂images
 ┃ ┣ 📂string_dtw
 ┃ ┗ 📂platoons
 ┣ 📂src
 ┃ ┣ 📜analyze_platoon_life.py
 ┃ ┣ 📜compare_DTW_ACC_HDV.py
 ┃ ┣ 📜compute_half_life.py
 ┃ ┣ 📜detect_string_instability_platoon.py
 ┃ ┣ 📜examine_string_instability.py
 ┃ ┣ 📜read_data.py
 ┃ ┣ 📜test_CF.py
 ┃ ┗ 📜test_platoon.py
 ┣ 📜.gitignore
 ┣ 📜README.md
 ┗ 📜console.ipynb
```


To install the necessary packages follow the following guidelines, be aware that they differ whether you are a Windows user or a Unix kernel-based OS user.

### Unix distributions/MacOS installation

Copy your local path to this repository
Then open the command prompt
````bash
cd %paste your path
````

````bash
conda env create -f conda/env.yaml
````

Activate it:
````bash
conda activate platoon_env
````

You can then run the commands in the console.ipynb file 

### Windows installation
Copy your local path to this repository
Open Anaconda navigator
Open CMD.exe prompt and type
````bash
cd %paste your path
````

then type 
````bash
conda env create -f conda/ACC_fuel_windows.yml
````

Activate it:
````bash
conda activate platoon_env
````

You can then run the commands in the console.ipynb file 

## How to use this code
You have two chaoices, either reuse the results and recreate the analysis results or launch the platoon detection and recreate all inputs for results analysis.<br>
Once you have downloaded the data, we suggest you to create a 'data' folder and to place the data in it.<br>
The code is run from the 'Console.ipynb' notebook.<br>

Sourcecode can be changed, the python files are in the 'src' folder.<be>

## Licence
This code is under licence EUPL-1.2.




