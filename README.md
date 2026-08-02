# WxBox FV3-JEDI Demonstrations

This S3 repository contains reproducible FV3-JEDI demonstration workflows built with the WxBox Stack.

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
    jongmantari/wxbox-fv3jedi:5a0d925-tools
```

Launch:

```bash
docker run -it --rm \
    -v ~/.aws:/root/.aws:ro \
    -v $PWD:$PWD \
    -w $PWD \
    jongmantari/wxbox-fv3jedi:5a0d925-tools \
    bash
```

Load the environment:

```bash
module use /home/wxbox_stack/modulefiles

module load jedi/5a0d925
```

Verify:

```bash
which wxbox-letkf
which wxbox-plot
which wxbox-movie
```

---

# Available Command Line Tools

## Grid

```bash
wxbox-create-grid
wxbox-create-mosaic
```

## HRRR

```bash
wxbox-download-hrrr
wxbox-hrrr-to-fv3
```

## Ensemble

```bash
wxbox-gen-ens
```

## Observation Database

```bash
wxbox-build-obsdb
```

## LETKF

```bash
wxbox-letkf
```

## Diagnostics

```bash
wxbox-plot
wxbox-density
wxbox-movie
```

---

# Available Demonstrations

List available demos:

```bash
aws s3 ls \
    s3://mantari-wxbox-fv3jedi/demos/ \
    --profile mantari
```

---

# Download a Demonstration

Example:

```bash
aws s3 sync \
    s3://mantari-wxbox-fv3jedi/demos/letkf_demo \
    ./letkf_demo \
    --profile mantari
```

Enter:

```bash
cd letkf_demo
```

---

# LETKF Demonstration

Example workflow:

```bash
wxbox-build-obsdb asos_concat.yaml

wxbox-gen-ens ensemble_c1667.yaml

wxbox-letkf run \
    configs/experiments/c1667.yaml

wxbox-plot run \
    configs/experiments/c1667.yaml

wxbox-density \
    configs/experiments/c1667.yaml

wxbox-movie \
    configs/experiments/c1667.yaml
```

---

# Repository Structure

```text
s3://mantari-wxbox-fv3jedi/

├── README.md
└── demos/
    ├── letkf_demo/
    ├── 2dvar_demo/
    └── ...
```

---

# Resources

## Docker Hub

https://hub.docker.com/u/jongmantari

## GitHub

https://github.com/jongmantari/wxbox_configs

## S3 Bucket

s3://mantari-wxbox-fv3jedi