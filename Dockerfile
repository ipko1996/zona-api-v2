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

# Create the ~/.EasyOCR/model directory and download the model file into it
RUN mkdir -p /home/seluser/.EasyOCR/model && \
    wget -O /home/seluser/.EasyOCR/model/craft_mlt_25k.zip https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip && \
    unzip /home/seluser/.EasyOCR/model/craft_mlt_25k.zip -d /home/seluser/.EasyOCR/model/ && \
    chown -R seluser:seluser /home/seluser/.EasyOCR

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
