ARG PORT=443

FROM selenium/standalone-firefox:111.0-geckodriver-0.33-20230403

USER root

RUN apt-get update && apt-get install -y python3 python3-pip git

RUN echo $(python3 -m site --user-base)

COPY requirements.txt .

ENV PATH /home/root/.local/bin:${PATH}

RUN pip install --upgrade pip && pip install -r requirements.txt

# Install EasyOCR from GitHub
RUN pip install git+https://github.com/JaidedAI/EasyOCR.git

# Download the craft_mlt_25k.zip file directly and extract its contents to ~/.EasyOCR/model folder
RUN mkdir -p /home/seluser/.EasyOCR/model && \
    wget -O /home/seluser/.EasyOCR/model/craft_mlt_25k.zip https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip && \
    unzip /home/seluser/.EasyOCR/model/craft_mlt_25k.zip -d /home/seluser/.EasyOCR/model/ && \
    rm /home/seluser/.EasyOCR/model/craft_mlt_25k.zip

# Download the latin_g2.zip file directly and extract its contents to ~/.EasyOCR/model folder
RUN wget -O /home/seluser/.EasyOCR/model/latin_g2.zip https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/latin_g2.zip && \
    unzip /home/seluser/.EasyOCR/model/latin_g2.zip -d /home/seluser/.EasyOCR/model/ && \
    rm /home/seluser/.EasyOCR/model/latin_g2.zip

RUN chown -R seluser:seluser /home/seluser/.EasyOCR

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
