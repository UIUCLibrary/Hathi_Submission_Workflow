.PHONY: all test gui install-dev
all: install-dev gui

install-dev:
	@pip install -r requirements.txt

gui:
	@echo "Converting Qt .ui files into Python files"
	@pyuic5 ui/ui_packages.ui -o hsw/ui/ui_packages.py

test: install-dev
	@python setup.py test
