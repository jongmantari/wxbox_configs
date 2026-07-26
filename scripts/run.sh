#mkdir -p ~/runs/hofx_rrfs
#cd ~/runs/hofx_rrfs

#cp -r ~/jedi-bundle/build/fv3-jedi/test/testinput .
#ln -s ~/jedi-bundle/build/fv3-jedi/test/Data Data

module purge
module load jedi/5a0d925

mpiexec --allow-run-as-root -n 12 $JEDI_BUNDLE_ROOT/bin/fv3jedi_hofx_nomodel.x hofx_nomodel_lam_c417.yaml

mpiexec --allow-run-as-root -n 12 $JEDI_BUNDLE_ROOT/bin/fv3jedi_error_covariance_toolbox.x bump_c417.yaml

mpiexec --allow-run-as-root -n 12 $JEDI_BUNDLE_ROOT/bin/fv3jedi_var.x 3dvar_lam_c417.yaml


