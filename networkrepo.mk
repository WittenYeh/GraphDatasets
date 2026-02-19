#common make file fragment for networkrepository.com
#just define GRAPH_NAME prior to including this fragment

GRAPH_ZIP  = $(GRAPH_NAME).zip
MTX2CSV    = ../mtx2csv.py

setup: nodes.csv edges.csv

nodes.csv edges.csv: $(GRAPH_NAME).mtx
	python3 $(MTX2CSV) $(GRAPH_NAME).mtx

$(GRAPH_NAME).mtx:
	$(WGET) $(GRAPH_URL)
	unzip $(GRAPH_ZIP)
	rm -f $(GRAPH_ZIP)

clean:
	rm -f $(GRAPH_NAME).mtx nodes.csv edges.csv
	rm -f readme.txt

realclean: clean
	@echo "All files cleaned (zip already removed during setup)"


