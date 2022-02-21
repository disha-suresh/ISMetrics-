SHELL:= /bin/bash

.PHONY: run
run: 
	docker-compose up --build --remove-orphans