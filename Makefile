########################################################

# Makefile for re-worker-satellite5
#
# useful targets (not all implemented yet!):
#   make clean               -- Clean up garbage
#   make pyflakes, make pep8 -- source code checks
#   make test ----------------- run all unit tests (export LOG=true for /tmp/ logging)

########################################################

# > VARIABLE = value
#
# Normal setting of a variable - values within it are recursively
# expanded when the variable is USED, not when it's declared.
#
# > VARIABLE := value
#
# Setting of a variable with simple expansion of the values inside -
# values within it are expanded at DECLARATION time.

########################################################


NAME := re-worker-satellite5
SHORTNAME := replugin
TESTPACKAGE := replugin

RPMSPECDIR := ./contrib/rpm/
RPMSPEC := $(RPMSPECDIR)/re-worker-satellite5.spec

sdist: clean
	python setup.py sdist
	rm -fR $(SHORTNAME).egg-info

virtualenv:
	@echo "#############################################"
	@echo "# Creating a virtualenv"
	@echo "#############################################"
	virtualenv $(NAME)env
	. $(NAME)env/bin/activate && pip install -r requirements.txt
	. $(NAME)env/bin/activate && pip install pep8 nose coverage mock
	# If there are any special things to install do it here
	. $(NAME)env/bin/activate && pip install git+https://github.com/RHInception/re-worker.git

ci-unittests:
	@echo "#############################################"
	@echo "# Running Unit Tests in virtualenv"
	@echo "#############################################"
	. $(NAME)env/bin/activate && nosetests -v --with-cover --cover-min-percentage=80 --cover-package=$(TESTPACKAGE) test/

ci-list-deps:
	@echo "#############################################"
	@echo "# Listing all pip deps"
	@echo "#############################################"
	. $(NAME)env/bin/activate && pip freeze

ci-pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests in virtualenv"
	@echo "#############################################"
	. $(NAME)env/bin/activate && pep8 --ignore=E501,E121,E124 $(SHORTNAME)/

ci: clean virtualenv ci-list-deps ci-pep8 ci-unittests
	:


tests: unittests pep8 pyflakes
	:

unittests:
	@echo "#############################################"
	@echo "# Running Unit Tests"
	@echo "#############################################"
	nosetests -v --with-cover --cover-min-percentage=80 --cover-package=$(TESTPACKAGE) test/


clean:
	@find . -type f -regex ".*\.py[co]$$" -delete
	@find . -type f \( -name "*~" -or -name "#*" \) -delete
	@rm -fR build dist rpm-build MANIFEST htmlcov .coverage $(SHORTNAME).egg-info reworkersatellite5.egg-info
	@rm -rf $(NAME)env

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	pep8 --ignore=E501,E121,E124 $(SHORTNAME)/

pyflakes:
	@echo "#############################################"
	@echo "# Running Pyflakes Sanity Tests"
	@echo "# Note: most import errors may be ignored"
	@echo "#############################################"
	-pyflakes src/$(SHORTNAME)

rpmcommon: sdist
	@mkdir -p rpm-build
	@cp dist/*.gz rpm-build/

srpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %{_topdir}" \
	-bs $(RPMSPEC)
	@echo "#############################################"
	@echo "Re-Core SRPM is built:"
	@find rpm-build -maxdepth 2 -name 're-worker-satellite5*src.rpm' | awk '{print "    " $$1}'
	@echo "#############################################"

rpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %{_topdir}" \
	-ba $(RPMSPEC)
	@echo "#############################################"
	@echo "Re-Core RPMs are built:"
	@find rpm-build -maxdepth 2 -name 're-worker-satellite5*.rpm' | awk '{print "    " $$1}'
	@echo "#############################################"
