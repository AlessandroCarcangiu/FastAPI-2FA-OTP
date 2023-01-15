# -------------------------------------
# Based on
# -------------------------------------

  FROM python:3.10



# -------------------------------------
# INFO
# -------------------------------------

  MAINTAINER "Alessandro Carcangiu"
  LABEL author="Alessandro Carcangiu"
  LABEL author_email="sandro.carcangiu@gmail.com"
  LABEL author_nickname="carca.ale"
  LABEL project="Login2FA"
  LABEL version = "0.1.0"



# -------------------------------------
# Packages
# -------------------------------------

  RUN apt-get update && \
      apt-get install -y \
      binutils \
      gettext



# -------------------------------------
# Install Requirements
# -------------------------------------
  ARG FASTAPI_USERS_REQUIREMENTS=base.txt
  ARG FASTAPI_USERS_REQUIREMENTS_FOLDER=./webapp/requirements/

  RUN mkdir -p ${FASTAPI_USERS_REQUIREMENTS_FOLDER}
  COPY requirements/* ${FASTAPI_USERS_REQUIREMENTS_FOLDER}
  RUN pip install -r ${FASTAPI_USERS_REQUIREMENTS_FOLDER}${FASTAPI_USERS_REQUIREMENTS}



# -------------------------------------
# Setup the working Directory
# -------------------------------------
  RUN mkdir -p /webapp
  WORKDIR /webapp/



# -------------------------------------
# Copy the webApp Code
# -------------------------------------

  COPY ./ ./