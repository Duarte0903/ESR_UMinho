# Variáveis globais
DISPLAY := :0
SRC_DIR := src
PYTHON := python3

# Argumentos
SERVER_ID ?= server1

# Exec

client:
	DISPLAY=$(DISPLAY) $(PYTHON) $(SRC_DIR)/OClient.py

node:
	DISPLAY=$(DISPLAY) $(PYTHON) $(SRC_DIR)/ONode.py

server:
	DISPLAY=$(DISPLAY) $(PYTHON) $(SRC_DIR)/Server.py $(SERVER_ID)

visualizer:
	DISPLAY=$(DISPLAY) $(PYTHON) $(SRC_DIR)/dynamicView.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete