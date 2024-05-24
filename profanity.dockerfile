FROM python:3.8

WORKDIR /app
COPY ./profanity_filter ./profanity_filter
COPY ./proto ./proto
COPY ./main.py ./main.py
COPY ./requirements.txt ./requirements.txt

# Устанавливаем зависимости
RUN pip3 install --no-cache-dir -r requirements.txt
# RUN python3 -m spacy download ru_core_news_md
RUN python3 -m spacy download en

# Запускаем main.py при старте контейнера
CMD ["python3", "./main.py"]
