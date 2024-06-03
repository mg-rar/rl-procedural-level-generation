# Состязательное обучение с подкреплением для процедурной генерации уровней

## Описание
Этот репозиторий содержит код и ресурсы для проекта, который использует алгоритм обучения с подкреплением Dueling Deep Q-Network для процедурной генерации уровней для 2D roguelike-игры. В проекте реализованы четыре RL-агента: генератор стен, генератор предметов, генератор врагов и решатель. Каждый из генераторов создает объекты на уровне, после чего он проходится решателем. Награды распределяются между генераторами и решателем в зависимости от успешности прохождения, тем самым побуждая агентов-генераторов создавать проходимые уровни. 

## Установка
pip install -r requirements.txt

## Использование
Цикл обучения агентов запускается из \_\_main\_\_ в файле main.py. Чтобы поиграть в игру в тестовом режиме с клавиатуры, можно запустить ее из \_\_main\_\_ в game.py. В этом случае уровни будут заполняться случайно.