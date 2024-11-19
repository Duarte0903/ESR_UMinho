# Variáveis globais
DISPLAY := :0
SRC_DIR := src
PYTHON := python3

# Exec

client:
	DISPLAY=$(DISPLAY) $(PYTHON) $(SRC_DIR)/ClientLauncher.py

node:
	DISPLAY=$(DISPLAY)

server:
	DISPLAY=$(DISPLAY)

clean: