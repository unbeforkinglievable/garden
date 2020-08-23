ENV=development

.PHONY: all build build-frontend build-backend clean clean-frontend clean-backend backend frontend
.DEFAULT: all

all: build

build: build-frontend build-backend

build-frontend:
	cd garden_frontend && yarn build

build-backend: clean-backend
	python3 setup.py sdist

backend:
	FLASK_APP=garden_backend.app FLASK_ENV=$(ENV) python3 -m flask run #--cert=adhoc

frontend:
	cd garden_frontend && yarn start

clean: clean-frontend clean-backend

clean-backend:
	rm -rf dist *.egg-info

clean-frontend:
	cd garden_frontend && yarn clean

