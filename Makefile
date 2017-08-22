.PHONY: ui
init:
	@pip install -r requirements.txt

gui:
	@echo "Converting Qt .ui files into Python files"
	@pyuic5 ui/ui_packages.ui -o hsw/ui_packages.py

test:
	@python setup.py test
