FROM python

RUN mkdir /code
COPY ./requirements.txt /code
WORKDIR /code

RUN pip install -r requirements.txt

RUN mkdir /start
COPY ./run.sh /start
RUN chmod +x /start/run.sh

RUN useradd limitado -s /bin/bash
USER limitado

CMD /start/run.sh

