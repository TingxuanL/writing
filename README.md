## Purpose

This online writing education platform is designed to enhance students' writing skills and foster more effective interaction between students and teachers.

Its core objectives include:

1. Enabling teachers to create and grade writing assignments online;

2. Allowing students to complete assignments directly within their web browsers;

3. Capturing and replaying students’ writing processes—such as pauses between words or sentences—to extract key behavioral features that help teachers provide targeted feedback and instructional strategies.

The platform is a web-based application built on [the Django framework](https://www.djangoproject.com/). It is accessible through any browser on any operating system. Additionally, it can be deployed locally within a closed educational environment to safeguard sensitive data and prevent potential internet-related data leaks.

We have successfully collected data from over 200 students using our platform.

## Installation

The platform only needs to be installed on the server side. We recommend using [the Conda environment](https://docs.conda.io/projects/conda/en/latest/index.html). Please refer to the official installation instructions. 
After installing conda, you may use the following command to install the runtime environment.

```bash
# Clone this repo
git clone https://github.com/TingxuanL/writing.git
# Enter the repo
cd writing
# Create the environment
conda env create -f environment.yml
```

For illustration, we use the lightweight web server in Django. On the server side, run the following commands.

```bash
# Activate the environment
conda activate writing
python manage.py collectstatic --no-input
python manage.py runserver 0:8000
```

On the server side, open a browser ([Chrome](https://www.google.com/chrome/) is recommended) and visit <http://localhost:8000/accounts/login/?next=/writing/dashboard/>

On the client side, visit http://SERVER-IP:8000/accounts/login/?next=/writing/dashboard/. Note that one should use the server's correct IP address.

## Use

Please refer to [our wiki pages](https://github.com/TingxuanL/writing/wiki) for instructions on how to use the platform.


