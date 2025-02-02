include Make_linux.inc
#include Make_msys2.inc
#include Make_osx.inc

CXXFLAGS = -std=c++14
ifdef DEBUG
CXXFLAGS += -g -O0 -Wall -fbounds-check -pedantic -D_GLIBCXX_DEBUG
CXXFLAGS2 = CXXFLAGS
else
CXXFLAGS2 = ${CXXFLAGS}  
CXXFLAGS += -O3 -march=native -Wall
endif

ALL= calcul_pi.exe TestProductMatrix.exe test_product_matrice_blas.exe 

default:	help

all: $(ALL)

clean:
	@rm -fr *.o *.exe *~

.cpp.o:
	$(CXX) $(CXXFLAGS2) -c $^ -o $@	

calcul_pi.exe: calcul_pi.cpp
	$(MPICXX) $(CXXFLAGS) $^ -o $@

TestProductMatrix.exe : TestProductMatrix.o Matrix.hpp Matrix.o ProdMatMat.o
	$(CXX) $(CXXFLAGS2) $^ -o $@ $(LIB)	

test_product_matrice_blas.exe : test_product_matrice_blas.o Matrix.hpp Matrix.o
	$(CXX) $(CXXFLAGS2) $^ -o $@ $(LIB)	$(BLAS)

help:
	@echo "Available targets : "
	@echo "    all            : compile all executables"
	@echo "Add DEBUG=yes to compile in debug"
	@echo "Configuration :"
	@echo+= -g -O0 -Wall -fbounds-check -pedantic -D_GLIBCXX_DEBUG

ALL= calcul_pi.exe TestProductMatrix.exe test_product_matrice_blas.exe 

default:	help
 "    CXX      :    $(CXX)"
	@echo "    CXXFLAGS :    $(CXXFLAGS)"

%.html: %.md
	pandoc -s --toc $< --css=./github-pandoc.css --metadata pagetitle="OS202 - TD1" -o $@

run_tests_ProdMat: TestProductMatrix.exe
	@for i in $$(seq 1 16); do \
		echo "Running with OMP_NUM_THREADS=$$i"; \
		OMP_NUM_THREADS=$$i ./TestProductMatrix.exe $(n); \
    done

run_tests_ProdBlas: test_product_matrice_blas.exe
	@for i in $$(seq 1 16); do \
		echo "Running with OMP_NUM_THREADS=$$i"; \
		OMP_NUM_THREADS=$$i ./test_product_matrice_blas.exe $(n); \
    done