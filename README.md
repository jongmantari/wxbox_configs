WxBox FV3-JEDI Demonstrations
This S3 repository contains reproducible FV3-JEDI demonstration workflows built with the WxBox Stack.
Requirements
Docker
```bash
docker --version
```
AWS CLI
```bash
aws --version
```
Configure credentials:
```bash
aws configure --profile mantari
aws sts get-caller-identity --profile mantari
```
Docker Image
```bash
docker pull jongmantari/wxbox-fv3jedi:5a0d925-tools-v0.1
```
Download Demonstration
```bash
aws s3 sync \
    s3://mantari-wxbox-fv3jedi/demos/letkf_demo \
    ./letkf_demo \
    --profile mantari

cd letkf_demo
```
Launch Container
```bash
docker run -it --rm \
    -v $PWD:$PWD \
    -w $PWD \
    jongmantari/wxbox-fv3jedi:5a0d925-tools-v0.1 \
    bash
```
Initialize Environment
```bash
source /entrypoint.sh
module use /home/wxbox_stack/modulefiles
module load jedi/5a0d925
```
Verify:
```bash
which wxbox-letkf
which wxbox-gen-ens
which wxbox-plot
which wxbox-density
which wxbox-movie
```
Run LETKF Demonstration
Generate ensemble members:
```bash
wxbox-gen-ens ensemble_c1667.yaml
```
Validate:
```bash
wxbox-letkf check configs/experiments/c1667.yaml
```
Run LETKF:
```bash
wxbox-letkf run configs/experiments/c1667.yaml
```
Generate diagnostics:
```bash
wxbox-plot run configs/experiments/c1667.yaml
```
Generate innovation density:
```bash
wxbox-density configs/experiments/c1667.yaml
```
Generate movies:
```bash
wxbox-movie configs/experiments/c1667.yaml
```
WxBox Utilities
Grid:
```bash
wxbox-create-grid grid.yaml
wxbox-create-mosaic grid.yaml
```
HRRR:
```bash
wxbox-download-hrrr hrrr_download.yaml
wxbox-hrrr-to-fv3 hrrr_fv3.yaml
```
Observation Database:
```bash
wxbox-build-obsdb obsdb.yaml
```
LETKF:
```bash
wxbox-letkf check experiment.yaml
wxbox-letkf render experiment.yaml
wxbox-letkf run experiment.yaml
wxbox-letkf clean experiment.yaml
```
Diagnostics:
```bash
wxbox-plot run experiment.yaml
wxbox-plot summary experiment.yaml
wxbox-density experiment.yaml
wxbox-movie experiment.yaml
```
Notes
AWS CLI is only required on the host machine.
AWS CLI is not required inside the Docker container.
The LETKF demo includes a pre-generated observation database.
Demonstrations run entirely from locally downloaded data.
