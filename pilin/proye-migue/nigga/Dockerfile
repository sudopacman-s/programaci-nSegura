FROM python:latest

RUN apt-get update && apt-get install -y default-mysql-client

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --upgrade pip
RUN pip install  --resume-retries 5 -r ./requirements.txt

COPY ./proyecto /code

RUN mkdir /start

COPY start.sh /start

RUN chmod +x /start/start.sh

RUN mkdir /prueba 

#RUN groupadd -g 994 docker
#RUN useradd -u 1000 miguel -ms /bin/bash
#RUN chown miguel:miguel -R /prueba 
RUN useradd miguel -s /bin/bash

#RUN usermod -aG docker miguel

USER miguel

CMD ["bash","/start/start.sh"]
