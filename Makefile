# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

options = -N -q -t 3
pep8_ignores = E501
src = src/openmultimedia/utils/
minimum_coverage = 41

prerequisites:
	sudo apt-get install -q pep8 pyflakes
	pip install -q createzopecoverage
	mkdir -p buildout-cache/downloads

install: prerequisites
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(options)

tests:
	bin/test
	pep8 --ignore=$(pep8_ignores) $(src)
	pyflakes $(src)
	./coverage.sh $(minimum_coverage)
