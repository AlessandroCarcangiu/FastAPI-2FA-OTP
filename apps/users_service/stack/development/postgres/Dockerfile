# ------------------------------------- 
# Based on
# ------------------------------------- 

  FROM postgres:12


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
      apt-get install postgresql-12 -y

# ------------------------------------- 
# Add Postrgres INIT
# ------------------------------------- 

  ADD ./ ./
