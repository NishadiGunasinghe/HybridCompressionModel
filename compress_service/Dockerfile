# Use the latest Windows Server Core image as the base
FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

# Verify the installation
RUN python --version

WORKDIR /app
COPY . .
RUN pip --no-cache-dir install --ignore-installed distlib -r requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install zstd
CMD ["python", "Main.py"]