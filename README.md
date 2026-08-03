# WxBox FV3-JEDI Demonstrations

This S3 repository contains reproducible FV3-JEDI demonstration workflows built with the WxBox Stack.

The demonstrations use:

- FV3-JEDI
- JEDI LETKF
- HRRR background generation
- Ensemble generation
- IODA observation databases
- Diagnostics and verification
- Movie generation

---

# Requirements

## Docker

Verify:

```bash
docker --version
```

## AWS CLI

Verify:

```bash
aws --version
```

Configure Mantari credentials:

```bash
aws configure --profile mantari
```

Verify:

```bash
aws sts get-caller-identity \
    --profile mantari
```

---

# Docker Image

Pull the recommended image:

```bash
docker pull \
    jongmantari/wxbox-fv3jedi:5a0d925-tools-v0.1
```

---

# Download Demonstration

List available demonstrations:

```bash
aws s3 ls \
    s3://mantari-wxbox-fv3jedi/demos/ \
    --profile mantari
```

Download the LETKF demonstration:

```bash
aws s3 sync \
    s3://mantari-wxbox-fv3jedi/demos/letkf_demo \
    ./letkf_demo \
    --profile mantari
```

Enter the demonstration directory:

```bash
cd letkf_demo
```

---

# Launch Container

Start the Docker container from inside the demonstration directory:

```bash
docker run -it --rm \
    -v $PWD:$PWD \
    -w $PWD \
    jongmantari/wxbox-fv3jedi:5a0d925-tools-v0.1 \
    bash
```

---

# Initialize Environment

Inside the container:

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

---

# Run LETKF Demonstration

The demonstration already contains a pre-generated observation database.

## 1. Generate Ensemble Members

```bash
wxbox-gen-ens \
    ensemble_c1667.yaml
```

Generated:

```text
runs/c1667/<cycle>/ensemble/
```

---

## 2. Validate Experiment

```bash
wxbox-letkf check \
    configs/experiments/c1667.yaml
```

---

## 3. Run LETKF

```bash
wxbox-letkf run \
    configs/experiments/c1667.yaml
```

Generated:

```text
runs/c1667/<cycle>/letkf/
```

---

## 4. Generate Diagnostics

```bash
wxbox-plot run \
    configs/experiments/c1667.yaml
```

Generated:

```text
runs/c1667/<cycle>/letkf/post/
```

---

## 5. Generate Innovation Density

```bash
wxbox-density \
    configs/experiments/c1667.yaml
```

Generated:

```text
runs/c1667/post/experiment_density.png
```

---

## 6. Generate Movies

```bash
wxbox-movie \
    configs/experiments/c1667.yaml
```

Generated:

```text
runs/c1667/post/*.mp4
```

---

# Workflow Overview

```text
Observation Database
        ↓
wxbox-gen-ens
        ↓
Ensemble Members
        ↓
wxbox-letkf
        ↓
LETKF Analysis
        ↓
wxbox-plot
        ↓
Diagnostics
        ↓
wxbox-density
        ↓
Innovation Density
        ↓
wxbox-movie
        ↓
MP4 Animations
```

---

# WxBox Utilities Reference

The Docker image provides the following utili*ies.

## Grid Utilities

Generate *SG/FV3 regional grids:

```bash
wx*ox-create-grid grid.yaml
```

Gene*ate FV3 mosaics:

```bash
wxbox-cr*ate-mosaic grid.yaml
```

Typical *utputs:

```text
C1667_grid.tile7.*c

grid_spec.tile7.halo3.nc
```

-*-

## HRRR Utilities

Download HRR* analyses:

```bash
wxbox-download*hrrr hrrr_download.yaml
```

Conve*t HRRR analyses to FV3 restart fil*s:

```bash
wxbox-hrrr-to-fv3 hrrr*fv3.yaml
```

Typical outputs:

``*text
fv3_restart/

├── hrrr.fv_cor*.res.tile1.nc
├──*hrrr.fv_tracer.res.tile1.nc
├──*hrrr.fv_srf*wnd.res.tile1.nc
├──*hrrr.sfc_data.nc
└── *.coupler.res*```

---

## Ensemble Utilities*
Generate synthetic ensemble membe*s:

```bash
wxbox-gen-ens ensemble*yaml
```

Outputs:

```text
runs/<*xperiment>/<cycle>/ensemble/

├── *em01
├── mem02
├── mem03
├── mem04*└── mem05
```

---

## Observation*Database Utilities

Build cycle*aware IODA databases:

```bash
wxb*x-build-obsdb obsdb.yaml
``*

Outputs:

```text
runs/*bsdb/asos/

└── <cycle>/
    └*─*iem_asos_obs_<cycle>.nc4
```

---
**# LETKF Utilities

Validate experi*ent:

```bash
wxbox-let*f check experiment.yaml
```

Rende* JEDI YAML files:

```bash
wxbox-l*tkf render experiment.yaml
```

Ru* cycling:

```bash
wxbox-letkf run*experiment.yaml
```

Clean generat*d products:

```bash
wxbox-letkf c*ean experiment.yaml
```

---

## D*agnostic Utilities

Generate cycle*diagnostics:

```bash
wxbox-plot r*n experiment.yaml
```

Generate ex*eriment summary diagnostics:

```b*sh
wxbox-plot summary experiment.y*ml
```

Generate innovation densit*:

```bash
wxbox-density experimen*.yaml
```

Generate MP4 movies:

`*`bash
wxbox-movie experiment.yaml
*``

---

# Repository Structure

`*`text
s3://mantari-wxbox-fv3jedi/
*├── README.md
└── demos/
    ├── l*tkf_demo/
    ├── 2dvar_demo/
    *── ...
```

---

# Notes

- AWS CL* is required only on the host syst*m for downloading demonstrations.
* AWS CLI is not required inside th* Docker container.
- The Docker im*ge is platform independent and con*ains all required WxBox utilities.*- Demonstrations are designed to r*n entirely from locally downloaded*data.
- The LETKF demonstration in*ludes a pre-generated observation *atabase.

---

# Resources

## Doc*er Hub

https://hub.docker.com/u/j*ngmantari

## GitHub

https://gith*b.com/jongmantari/wxbox_configs

## S3 Bucket

```text
s3://mantari-wxbox-fv3jedi
```

---

Developed as part of the Mantari WxBox Stack FV3-JEDI workflow framework.
