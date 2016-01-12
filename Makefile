VERSION = 3.0.2
NAME = thingpin
DEB_PACKAGE = dist/$(NAME)_$(VERSION)_all.deb

BUMP = PYTHONPATH=src/misc bumpversion \
       --config-file src/misc/.bumpversion.cfg \
       --post-hook bump.hook

GEMFURY_API_TOKEN = `cat ~/.gemfury-token`

build: clean
	python setup.py sdist bdist_wheel

clean:
	$(RM) build dist *.egg-info .coverage htmlcov

very-clean: clean
	$(RM) .eggs .cache
	find . -name '*.pyc' | xargs rm -f

install:
	python setup.py install
	pip install \
	    pep8 \
	    mock \
		coveralls \
		freezegun \
		https://github.com/adafruit/io-client-python/zipball/65320a

install-dev:
	pip install https://github.com/mgk/bumpversion/zipball/post-hook

release: clean test
	$(BUMP) release
	python setup.py sdist bdist_wheel
	twine upload -r pypitest dist/*
	git push origin master --tags
	@echo
	@echo "so far so good..."
	@echo "wait for Travis green light, then:"
	@echo
	@echo "twine upload dist/thingpin-*"
	@echo "make gemfury-upload"
	@echo " --- Remove gemfury -dev releases as they are seen as latest ---"
	@echo
	@echo "do bump-minor or bump-patch before next release"

bump-patch:
	$(BUMP) --no-tag patch

bump-minor:
	$(BUMP) --no-tag minor

bump-major:
	$(BUMP) --no-tag major

test:
	pep8 setup.py src/thingpin
	py.test

coverage:
		coverage run --source=src/thingpin -m py.test
		coverage html

scp: deb
	scp $(DEB_PACKAGE) pi@pi2a.local:~/

deb: build
	fpm -s dir -t deb -a all \
  		-n $(NAME) -v $(VERSION) \
  		--package $(DEB_PACKAGE) \
  		--depends runit \
  		--template-scripts \
  		--after-install src/misc/fpm-after-install.sh \
  		`ls dist/*.tar.gz`=/tmp/$(NAME)-$(VERSION).tar.gz \
  		src/examples/etc/thingpin/=/etc/thingpin/ \
   	    src/examples/etc/service/thingpin/=/tmp/thingpin-service/

gemfury-upload:
	curl -F package=@$(DEB_PACKAGE) https://push.fury.io/$(GEMFURY_API_TOKEN)/

sign-install-script:
	gpg -ao install.asc --detach-sig install

.PHONY: build clean very-clean install install-dev release bump-patch \
	    bump-minor test scp deb
