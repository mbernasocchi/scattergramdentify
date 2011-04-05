all: package

package: clean
	git archive --format zip --output scattergrammidentify.zip --prefix=scattergrammidentify/ master
	
clean:
	rm -f *.pyc

