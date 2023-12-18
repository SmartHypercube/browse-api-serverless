all: deploy

artifacts: artifacts/puppeteer.zip artifacts/python.zip artifacts/browse-text.zip artifacts/github.zip artifacts/pdf.zip artifacts/youtube.zip

artifacts/puppeteer.zip: %.zip: package.json package-lock.json
	rm -rf $@ $*
	mkdir -p $*/nodejs/node_modules
	cp $^ $*/nodejs
	npm install --prefix $*/nodejs
	cd $* && zip -r ../$(@F) .

artifacts/python.zip: %.zip: requirements.txt
	rm -rf $@ $*
	mkdir -p $*
	python3 -m venv $*/python
	$*/python/bin/pip install -r $<
	cd $* && zip -r ../$(@F) .

artifacts/browse-text.zip: %.zip: browse-text.mjs
	rm -rf $@ $*
	mkdir -p $*
	cp $^ $*
	cd $* && zip -r ../$(@F) .

artifacts/github.zip: %.zip: github.py
	rm -rf $@ $*
	mkdir -p $*
	cp $^ $*
	cd $* && zip -r ../$(@F) .

artifacts/pdf.zip: %.zip: pdf.py
	rm -rf $@ $*
	mkdir -p $*
	cp $^ $*
	cd $* && zip -r ../$(@F) .

artifacts/youtube.zip: %.zip: youtube.py
	rm -rf $@ $*
	mkdir -p $*
	cp $^ $*
	cd $* && zip -r ../$(@F) .

deploy: artifacts
	sls deploy

clean:
	rm -rf artifacts

.PHONY: all artifacts deploy clean
