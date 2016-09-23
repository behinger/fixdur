CXX:=g++
#MATLAB:=/home/jss/bin/ml/bin/
MATLAB:=/opt/matlab/bin/
#MATLAB:=/Applications/_IKW/Matlab704/bin/
MEX:=$(MATLAB)mex -v
LDFLAGS:=-L$(MATLAB)glnx64 -L. -lm
SOURCE:=../../src/
INCLUDE:=../../include64/
default: edfread.mexglx

all: edfread.mexglx static

edfread.mexglx:
	$(MEX)  $(LDFLAGS) -DMEX -I$(SOURCE) -I$(INCLUDE)  $(SOURCE)edfread.cpp  $(LDFLAGS) -ledfapi 

static:
	$(CXX) -g $(SOURCE)edfread.cpp -o edfread.x86.static -I$(INCLUDE) -I$(SOURCE) $(LDFLAGS) -lgcc -ledfapi 
minimal:
	$(CXX) -g ../../src/minimal/main.cpp -o minimal -I../../src/ -I$(INCLUDE) $(LDFLAGS) -ledfapi
clean:
	rm -f edfread.mexglx
	rm -f edfread.x86.static
