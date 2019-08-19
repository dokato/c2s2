# Medical Cohort Selection
Python scripts with a competition solution prepared for "2018 N2C2 Shared Tasks".

Data to train the models is available upon request at https://n2c2.dbmi.hms.harvard.edu/.

## Setup

You might need the following to run these scripts:
```
- python 2.7
- numpy
- sklearn
- xgboost
- conreader (optional)
```
You might also need the following data structure:

```
clitri/
test_gold/
models/
runsequence.sh
README.md 
testoutput/
output/
```

where `clitri/` is the folder with scripts for training, testing models; `test_gold/` - is folder with annotation of the test files; `models/` is the folder where you keep trained ML models and vectorisers; `output/` output of training data (eg. for crossvalidation); `testoutput/` output of prediction on test set.


**!!!** You may change all paths to the files in `clitri/utils.py`.

## Running the preprocessing (feature extraction)

TODO

## Running the classification script

This script is intended to be used via command line:
```shell
$ ./runsequence.sh
```

It performs model trainign with `clitri/classifiers.py` script, model prediction with `clitri/discovry.py` and evaluation with 
`track1_eval.py`.

## Output for Track 1: Cohort Selection for Clinical Trials

Our best score:

```
                      ------------ met -------------    ------ not met -------    -- overall ---
                      Prec.   Rec.    Speci.  F(b=1)    Prec.   Rec.    F(b=1)    F(b=1)  AUC   
           Abdominal  0.6486  0.8000  0.7679  0.7164    0.8776  0.7679  0.8190    0.7677  0.7839
        Advanced-cad  0.8431  0.9556  0.8049  0.8958    0.9429  0.8049  0.8684    0.8821  0.8802
       Alcohol-abuse  0.1667  0.6667  0.8795  0.2667    0.9865  0.8795  0.9299    0.5983  0.7731
          Asp-for-mi  0.8571  0.9706  0.3889  0.9103    0.7778  0.3889  0.5185    0.7144  0.6797
          Creatinine  0.8000  0.8333  0.9194  0.8163    0.9344  0.9194  0.9268    0.8716  0.8763
       Dietsupp-2mos  0.7885  0.9318  0.7381  0.8542    0.9118  0.7381  0.8158    0.8350  0.8350
          Drug-abuse  0.4000  0.6667  0.9639  0.5000    0.9877  0.9639  0.9756    0.7378  0.8153
             English  0.9241  1.0000  0.5385  0.9605    1.0000  0.5385  0.7000    0.8303  0.7692
               Hba1c  1.0000  0.8000  1.0000  0.8889    0.8793  1.0000  0.9358    0.9123  0.9000
            Keto-1yr  0.0000  0.0000  1.0000  0.0000    1.0000  1.0000  1.0000    0.5000  0.5000
      Major-diabetes  0.8684  0.7674  0.8837  0.8148    0.7917  0.8837  0.8352    0.8250  0.8256
     Makes-decisions  0.9762  0.9880  0.3333  0.9820    0.5000  0.3333  0.4000    0.6910  0.6606
             Mi-6mos  0.3333  0.5000  0.8974  0.4000    0.9459  0.8974  0.9211    0.6605  0.6987
                      ------------------------------    ----------------------    --------------
     Overall (micro)  0.8360  0.9107  0.8756  0.8717    0.9337  0.8756  0.9037    0.8877  0.8931
     Overall (macro)  0.6620  0.7600  0.7781  0.6928    0.8873  0.7781  0.8189    0.7559  0.7691

```

The official ranking measure is Overall (micro) F(b=1) (0.8877).

### Criterion

In this study - based on a textual hisotry of patients - we wanted to predict if they meet or not the following medical criteria:

- Abdominal
- Advanced-cad
- Alcohol-abuse
- Asp-for-mi
- Creatinine
- Dietsupp-2mos
- Drug-abuse
- English
- Hba1c
- Keto-1yr
- Major-diabetes
- Makes-decisions
- Mi-6mos

### Details

For details of this approach, please referto this article: *SOON*.

If you use lexicons, or part of our code, please cite above-mentioned article.
