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
preproc/
```

where `clitri/` is the folder with scripts for training, testing models; `test_gold/` - is folder with annotation of the test files; `models/` is the folder where you keep trained ML models and vectorisers; `output/` output of training data (eg. for crossvalidation); `testoutput/` output of prediction on test set.


**!!!** You may change all paths to the files in `clitri/utils.py`.

## Running the preprocessing (feature extraction)

If you followed the directory structure from above, you should be able to navigate into the `preproc/` folder and simply call:

```
python preprocessing.py
```

You might want to also change `in_dir` variable from `preprocessing.py` script to the path containing the raw data:

```
# --- input files
in_dir = './00_input/'
```

All the lexicons used for data cleaning and filtering are available in `preproc/lexicon/` catalogue.

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
        Advanced-cad  0.8302  0.9778  0.7805  0.8980    0.9697  0.7805  0.8649    0.8814  0.8791
       Alcohol-abuse  0.2222  0.6667  0.9157  0.3333    0.9870  0.9157  0.9500    0.6417  0.7912
          Asp-for-mi  0.8767  0.9412  0.5000  0.9078    0.6923  0.5000  0.5806    0.7442  0.7206
          Creatinine  0.8000  0.8333  0.9194  0.8163    0.9344  0.9194  0.9268    0.8716  0.8763
       Dietsupp-2mos  0.7885  0.9318  0.7381  0.8542    0.9118  0.7381  0.8158    0.8350  0.8350
          Drug-abuse  0.4000  0.6667  0.9639  0.5000    0.9877  0.9639  0.9756    0.7378  0.8153
             English  0.9125  1.0000  0.4615  0.9542    1.0000  0.4615  0.6316    0.7929  0.7308
               Hba1c  1.0000  0.8286  1.0000  0.9062    0.8947  1.0000  0.9444    0.9253  0.9143
            Keto-1yr  0.0000  0.0000  1.0000  0.0000    1.0000  1.0000  1.0000    0.5000  0.5000
      Major-diabetes  0.8500  0.7907  0.8605  0.8193    0.8043  0.8605  0.8315    0.8254  0.8256
     Makes-decisions  0.9762  0.9880  0.3333  0.9820    0.5000  0.3333  0.4000    0.6910  0.6606
             Mi-6mos  0.3333  0.5000  0.8974  0.4000    0.9459  0.8974  0.9211    0.6605  0.6987
                      ------------------------------    ----------------------    --------------
     Overall (micro)  0.8397  0.9129  0.8786  0.8747    0.9354  0.8786  0.9061    0.8904  0.8957
     Overall (macro)  0.6645  0.7634  0.7799  0.6991    0.8850  0.7799  0.8201    0.7596  0.7716

```

The official ranking measure is Overall (micro) F(b=1) (0.8904).

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

For details of this approach, please refer to this article: *SOON*.

If you use lexicons, or part of our code, please cite above-mentioned article.
