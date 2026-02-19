#common make file fragment for ufl graph datasets
#just define GRAPH_NAME prior to including this fragment

GRAPH_TAR  = $(GRAPH_NAME).tar.gz
MTX2CSV    = ../mtx2csv.py

setup: nodes.csv edges.csv

nodes.csv edges.csv: $(GRAPH_NAME).mtx
	python3 $(MTX2CSV) $(GRAPH_NAME).mtx

$(GRAPH_NAME).mtx:
	$(WGET) $(GRAPH_URL)
	tar xvfz $(GRAPH_TAR)
	cp $(GRAPH_NAME)/$(GRAPH_NAME).mtx $(GRAPH_NAME).mtx
	rm -rf $(GRAPH_NAME)
	rm -f $(GRAPH_TAR)

clean:
	rm -f $(GRAPH_NAME).mtx nodes.csv edges.csv

realclean: clean
	@echo "All files cleaned (tar.gz already removed during setup)"


