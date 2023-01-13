# TAFFI-Drude
 Polarizable extension of TAFFI
# How to run
## Before Running
- made sure the openmpi is correctly loaded so that chosen ORCA version can be executed without any errors (or DFT jobs will just keep failing)

## nonpolar
- step 1. create a folder (e.g., /home/lin/nonpolar) and put the desired xyzs in it
- step 2. run taffi/Automation_scripts/driver.py -c config.txt (this is original code, it's not included here)
- step 3. When finished, you should have "Param_for_Batch.db" that contains the parameters

## Drude
### You can run this at the original nonpolar or create a new folder for it (e.g., polar)
- step 1. create a new folder (or alternatively just go to the nonpolar dir)
### Note: the drude_config.py is only written in this way so that all DFT calculations for each generation can be submitted parallelly, I have the other version which just did all these consecutively, it's slower but will save you from executing bash file for each generation, python would just do everything from the first generation to the last
- step 2. run taffi_drude/Automation_Scripts/drude_configs.py -c config.txt -nonpolar_dir /home/lin/nonpolar (replace with correct path) --write_bash
- step 3. "sh drude_gens.sh", this will create a screen session for each inchikey, and start the needed charge DFT
### make sure each model compound (inchikey)'s charge DFT jobs are finished, that is, each script has finished without error, sometimes you might need to restart since some DFT jobs might crash (I find this weird but it might be just way too many jobs so some failed on first try, but ran smoothly on second)
- step 4. run taffi_drude/Automation_Scripts/drude_fit.py -c config.txt -nonpolar_FF Params_for_Batch.db (replace with correct file) -nonpolar_dir /home/lin/nonpolar (replace with correct path)
### the result parameter will be at the folder that you execute drude_fit.py called "final_drude.db"
