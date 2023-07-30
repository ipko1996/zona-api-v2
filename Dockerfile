ARG PORT=443

FROM selenium/standalone-chrome:latest

USER root

RUN apt-get update && apt-get install -y python3 python3-pip git

RUN echo $(python3 -m site --user-base)

COPY requirements.txt .

ENV PATH /home/root/.local/bin:${PATH}

RUN pip install --upgrade pip && pip install -r requirements.txt

# Install EasyOCR from GitHub
RUN pip install git+https://github.com/JaidedAI/EasyOCR.git

# Create the ~/.EasyOCR/model directory
RUN mkdir -p /home/seluser/.EasyOCR/model

# Download the model file and place it in the ~/.EasyOCR/model folder
RUN wget -O /home/seluser/.EasyOCR/model/latin.zip https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/latin.zip

# Unzip the model file
RUN unzip /home/seluser/.EasyOCR/model/latin.zip -d /home/seluser/.EasyOCR/model/

# Set the correct permissions for the model folder
RUN chown -R seluser:seluser /home/seluser/.EasyOCR

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
