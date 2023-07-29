ARG PORT=443

FROM selenium/standalone-chrome:latest

RUN apt-get install python3 -y

RUN echo $(python3 -m site --user-base)

COPY requirements.txt  .

ENV PATH /home/root/.local/bin:${PATH}

RUN  apt-get update && apt-get install -y python3-pip && pip install -r requirements.txt  

RUN apt-get install -y git

# we need to install easyocr from github else it will not work
RUN pip install git+https://github.com/JaidedAI/EasyOCR.git

COPY . .

CMD hypercorn main:app --host 0.0.0.0 --port $PORT