# WxBox FV3-JEDI Demonstrations

This repository provides Docker-based FV3-JEDI demonstration workflows developed with the WxBox Stack.

The demonstrations include:

- Custom FV3 regional grid generation
- FV3 mosaic generation
- Background interpolation
- JEDI HofX workflows
- JEDI 2DVAR workflows
- BUMP covariance workflows
- Diagnostic plotting
- Docker deployment
- AWS S3 distribution

---

# 1. Install Docker

## Windows

Install Docker Desktop:

https://www.docker.com/products/docker-desktop/

Verify:

```powershell
docker --version
```

---

## Linux

```bash
curl -fsSL https://get.docker.com | sh
```

Verify:

```bash
docker --version
```

---

# 2. Install AWS CLI

## Linux

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
  -o awscliv2.zip

unzip awscliv2.zip

sudo ./aws/install
```

Verify:

```bash
aws --version
```

---

# 3. Configure AWS Credentials

Configure your Mantari AWS account:

```bash
aws configure --profile mantari
```

Verify:

```bash
aws sts get-caller-identity --profile mantari
```

Example:

```text
Account: 334566771276
Arn: arn:aws:iam::334566771276:user/jong
```

---

# 4. Download Docker Image

Docker Hub:

https://hub.docker.com/u/jongmantari

Pull the recommended image:

```bash
docker pull jongmantari/wxbox-fv3jedi:5a0d925-tools
```

---

# 5. Launch Container

Mount AWS credentials automatically:

```bash
docker run -it --rm \
  -v ~/.aws:/root/.aws:ro \
  -v $PWD:$PWD \
  -w $PWD \
  jongmantari/wxbox-fv3jedi:5a0d925-tools \
  bash
```

Inside the container:

```bash
module use /home/wxbox_stack/modulefiles

module load jedi/5a0d925
```

Verify environment:

```bash
python -c "import xarray"
python -c "import netCDF4"
python -c "import scipy"
python -c "import matplotlib"
python -c "import cartopy"
```

---

# 6. Download Demonstrations

Mantari S3 bucket:

```text
s3://mantari-wxbox-fv3jedi
```

Download the 2DVAR demonstration:

```bash
aws s3 sync \
  s3://mantari-wxbox-fv3jedi/demos/2dvar_demo \
  ./2dvar_demo
```

Enter the demonstration directory:

```bash
cd 2dvar_demo
```

---

# 7. Demonstration Contents

The package contains:

```text
create_esg_grid.py
create_mosaic.py
regrid_fv3_restart.py
plot_lam_analysis_obs.py

c417.yaml
c1667.yaml

bump_c417.yaml
bump_c1667.yaml

hofx_nomodel_c417.yaml
hofx_nomodel_c1667.yaml

analysis_c417/
analysis_c1667/

Data/
```

Supported domains:

- C417
- C1667

---

# 8. Grid Generation

Generate regional FV3 grids:

```bash
python create_esg_grid.py c417.yaml

python create_esg_grid.py c1667.yaml
```

---

# 9. Mosaic Generation

Create FV3 mosaic files:

```bash
python create_mosaic.py c417.yaml

python create_mosaic.py c1667.yaml
```

---

# 10. Background Interpolation

Generate FV3 restart backgrounds:

```bash
python regrid_fv3_restart.py c417.yaml

python regrid_fv3_restart.py c1667.yaml
```

---

# 11. Run 2DVAR Demonstration

```bash
./run_2dvar.sh
```

Included workflows:

- JEDI HofX
- BUMP covariance
- FV3-JEDI 2DVAR
- Aircraft observation assimilation

---

# 12. Generate Diagnostics

Generate diagnostic plots:

```bash
python plot_lam_analysis_obs.py \
  --config plot_c417.yaml
```

or

```bash
python plot_lam_analysis_obs.py \
  --config plot_c1667.yaml
```

Generated diagnostics include:

- Background field
- Analysis field
- OMB (Obs − Background)
- OMA (Obs − Analysis)
- Innovation density curves
- Innovation mean shift
- RMSE reduction

---

# 13. Docker Image

Recommended image:

```bash
docker pull jongmantari/wxbox-fv3jedi:5a0d925-tools
```

Inside container:

```bash
module use /home/wxbox_stack/modulefiles

module load jedi/5a0d925
```

---

# 14. S3 Repository

Bucket:

```text
s3://mantari-wxbox-fv3jedi
```

Demonstration:

```text
s3://mantari-wxbox-fv3jedi/demos/2dvar_demo
```

Documentation:

```text
README.md
README.html
```

---

# 15. Workflow Overview

```text
Custom Grid
      ↓
Mosaic
      ↓
Background Regridding
      ↓
HofX
      ↓
2DVAR
      ↓
Diagnostics
```

---

# Project Resources

## GitHub

https://github.com/jongmantari/wxbox_configs

## Docker Hub

https://hub.docker.com/u/jongmantari

## S3 Bucket

s3://mantari-wxbox-fv3jedi

---

Developed as part of the Mantari WxBox Stack FV3-JEDI workflow framework.
