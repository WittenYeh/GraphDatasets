#common make file fragment for networkrepository.com
#just define GRAPH_NAME prior to including this fragment

GRAPH_ZIP  = $(GRAPH_NAME).zip

setup: $(GRAPH_NAME).mtx

$(GRAPH_NAME).mtx: $(GRAPH_ZIP)
	unzip $(GRAPH_ZIP)
	rm -f $(GRAPH_ZIP)

clean:
	rm -f $(GRAPH_NAME).mtx
	rm -f readme.txt

realclean: clean
	@echo "All files cleaned (zip already removed during setup)"


