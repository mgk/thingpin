VERSION = 1.1.0-dev
NAME = thingpin
DEB = $(NAME)_$(VERSION)_all.deb

BUMP = PYTHONPATH=src/misc bumpversion \
       --config-file src/misc/.bumpversion.cfg \
       --post-hook bump.hook

build: clean
	python setup.py sdist bdist_wheel

clean:
	$(RM) build dist *.egg-info .coverage htmlcov $(DEB)

very-clean: clean
	$(RM) .eggs .cache
	find . -name '*.pyc' | xargs rm -f

install:
	python setup.py install

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
	@echo "twine upload dist/*"
	@echo
	@echo "do bump-minor or bump-patch before next release"

bump-patch:
	$(BUMP) --no-tag patch

bump-minor:
	$(BUMP) --no-tag minor

test:
	pep8 setup.py src/thingpin
	# py.test

scp: build
	scp dist/*.gz pi@pi2a.local:~/

deb: build
	fpm -s dir -t deb -a all \
  		-n $(NAME) -v $(VERSION) \
  		--after-install after-install.sh \
  		\
  		$(NAME).py=/usr/local/bin/ \
  		etc/init.d/$(NAME)=/etc/init.d/ \
  		etc/$(NAME)/$(NAME).conf=/etc/$(NAME)/

.PHONY: build clean very-clean install install-dev release bump-patch \
	    bump-minor test scp deb
