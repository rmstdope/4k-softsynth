.PHONY: softsynth editor all run_tests

all:
	$(MAKE) -C softsynth all
#	$(MAKE) -C editor all

run_tests:
	$(MAKE) -C softsynth run_tests
#	$(MAKE) -C editor run_tests


