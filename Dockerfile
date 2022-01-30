FROM python:3.9.10
WORKDIR /qdrant_celebrity_bot
COPY requirements.txt requirements.txt
COPY bot.py bot.py
COPY query.py query.py 
COPY cfg.yaml cfg.yaml
RUN pip install -r requirements.txt
RUN python query.py
CMD python bot.py