# Drude_config.py
## fit_Drude_custom:
### 1. place perturbation charges
- need: nonpolar inchikey/charges/CHELG_calcs/configs/n, n=0~100 each folders' xyz (up to 100 configurations)
- outside call: FF_functions/place_charge.py
- inside call: place_perturbation_submit, clean_pc_submit
- do: generate fitcharge_n folder and each folder's pointcharge.pc
- config[param_fit_q] and config[param_fit_t] is used

### 2. QM polar calculation
- need: nonpolar inchikey/charges/CHELG_calcs/configs/n, n=0~100 each folders' xyz (up to 100 configurations)
- outside call: Automation/orca_submit.py
- inside call: polar_orca
- do: ORCA polarizability and dipole calculation for later FOM to compare to, the result will be in polar.out in each fitcharge_n folder

### 3. CHELPG potential calculation 
- need: fitcharge_n/layer_n/pointcharge.pc from place_charge 
- outside call: Automation/orca_submit.py
- inside call: get_pc, calc_CHELPG, Write_charge_in, clean_chelpg
- do: ORCA CHELPG calculation with perturbation charge placed, will do this for e=0.5 and -0.5, the calculation result will be in config_0.5 and configs_-0.5 in each fitchage_n folder

### 4. Revaluation at Connolly grid
- need: fitchage_n/configs_+-0.5's gbw and scfp files
- outside call: FF_functions/generate_connolly.py, Automation/bundle_submit.py
- inside call: get_pc, get_connolly_grid, calc_connoly_pot, rewrite_potential, clean_connolly
- do: reevaluating charge potentail at desire grid using the already calculated potential
- config[module_string] is used

### 5. Rewrite reevaluation potential format
- need:
- outside call: None
- inside call: get_pc, get_connolly_grid, rewrite_pot_wrap, rewrite_potential
- do: this is already called during calc_connolly_pot, reexecuting to avoid ommission

### 6. Write out charmm fitting script for later
- need:
- outside call: None
- inside call: write_charmm_data, write_datadir
- do: write out fitting script for charmm to submit later

# Drude_fit.py 
### XXX: to be resolved: more function call than shell call here (need effciency test)
    # FF dependency:
    # input for:
    # 1. fitcharge.inp: intra_only,VDW_only,charge_only(for initial guess),lower gens' Drude
    # 2. VDW refit: extract_vdw: lower gens' local Drude, Drude charge just fitted
    #               initial_param.db (initial guess): original cycle-20 and lower gens' local Drude (cross term is needed for initial guess)
    # FF info:
    # 1. in each inchikey:
    #    inchikey/drude_Q.db <- Drude charge
    #    inchikey/vdw/vdw_drude/DFT-AA.db <- Drude reparametrize VDW (has cross term)
    # 2. in driver folder:
    #    genN_drude.db : Drude charge, Drude vdw for that generation (has cross term)
    #    total_drude: complete FF (no cross term)
## fit_Drude
### 1. Use CHARMM to fit charge for all configurations (from nonpolar) at same generation at once
- need:
- outside call: gen_md_for_charmm.py, bundle_submit.py
- inside call: write_fitinp, fit_exe
- do: write out CHARMM inp file for charge fitting and submitting jobs

### 2. Calculate average charge over all configurations
- need:
- outside call: log_to_db
- inside call: open_chi, write_chi, write_db
- do: average all configuration's refit charge and write out to drude_Q.db for each inchikey

### 3. VDW_re
- need:
- outside call: shell_submit.sh, extract_vdw_drude.py, relax_drude.py, db_to_charmm.py
- inside call: 
- do: algorithm the same, but reparametrizing by include the Drude particles in the dimer configurations -> relax -> include Drude charge, the fitted VDW would be total eng - electrostatic from Drude + normal atoms

### 4. Final merge all gen's drude db to final drude db
