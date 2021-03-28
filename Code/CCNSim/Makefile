#
# OMNeT++/OMNEST Makefile for CCNSim
#
# This file was generated with the command:
#  opp_makemake -f --deep -O out
#

# Name of target to be created (-o option)
TARGET = CCNSim$(EXE_SUFFIX)

# User interface (uncomment one) (-u option)
USERIF_LIBS = $(ALL_ENV_LIBS) # that is, $(TKENV_LIBS) $(CMDENV_LIBS)
#USERIF_LIBS = $(CMDENV_LIBS)
#USERIF_LIBS = $(TKENV_LIBS)

# C++ include paths (with -I)
INCLUDE_PATH = \
    -I. \
    -Iinclude \
    -Iini \
    -Imodules \
    -Imodules/clients \
    -Imodules/content \
    -Imodules/node \
    -Imodules/node/cache \
    -Imodules/node/strategy \
    -Imodules/statistics \
    -Inetworks \
    -Ipackets \
    -Iresults \
    -Iresults/abilene \
    -Iresults/abilene/F-spr \
    -Iresults/abilene/F-spr/D-lce \
    -Iresults/abilene/F-spr/D-lce/R-lru \
    -Iresults/abilene/F-spr/D-lce/R-lru/alpha-1 \
    -Isrc \
    -Isrc/clients \
    -Isrc/content \
    -Isrc/node \
    -Isrc/node/cache \
    -Isrc/node/strategy \
    -Isrc/statistics

# Additional object and library files to link with
EXTRA_OBJS =

# Additional libraries (-L, -l options)
LIBS =

# Output directory
PROJECT_OUTPUT_DIR = out
PROJECTRELATIVE_PATH =
O = $(PROJECT_OUTPUT_DIR)/$(CONFIGNAME)/$(PROJECTRELATIVE_PATH)

# Object files for local .cc and .msg files
OBJS = \
    $O/src/ctopology.o \
    $O/src/clients/client.o \
    $O/src/content/content_distribution.o \
    $O/src/content/zipf.o \
    $O/src/node/core_layer.o \
    $O/src/node/cache/base_cache.o \
    $O/src/node/cache/fifo_cache.o \
    $O/src/node/cache/lru_cache.o \
    $O/src/node/cache/random_cache.o \
    $O/src/node/cache/two_cache.o \
    $O/src/node/strategy/nrr.o \
    $O/src/node/strategy/nrr1.o \
    $O/src/node/strategy/parallel_repository.o \
    $O/src/node/strategy/random_repository.o \
    $O/src/node/strategy/spr.o \
    $O/src/node/strategy/strategy_layer.o \
    $O/src/statistics/statistics.o \
    $O/packets/ccn_data_m.o \
    $O/packets/ccn_interest_m.o

# Message files
MSGFILES = \
    packets/ccn_data.msg \
    packets/ccn_interest.msg

#------------------------------------------------------------------------------

# Pull in OMNeT++ configuration (Makefile.inc or configuser.vc)

ifneq ("$(OMNETPP_CONFIGFILE)","")
CONFIGFILE = $(OMNETPP_CONFIGFILE)
else
ifneq ("$(OMNETPP_ROOT)","")
CONFIGFILE = $(OMNETPP_ROOT)/Makefile.inc
else
CONFIGFILE = $(shell opp_configfilepath)
endif
endif

ifeq ("$(wildcard $(CONFIGFILE))","")
$(error Config file '$(CONFIGFILE)' does not exist -- add the OMNeT++ bin directory to the path so that opp_configfilepath can be found, or set the OMNETPP_CONFIGFILE variable to point to Makefile.inc)
endif

include $(CONFIGFILE)

# Simulation kernel and user interface libraries
OMNETPP_LIB_SUBDIR = $(OMNETPP_LIB_DIR)/$(TOOLCHAIN_NAME)
OMNETPP_LIBS = -L"$(OMNETPP_LIB_SUBDIR)" -L"$(OMNETPP_LIB_DIR)" -loppmain$D $(USERIF_LIBS) $(KERNEL_LIBS) $(SYS_LIBS)

COPTS = $(CFLAGS)  $(INCLUDE_PATH) -I$(OMNETPP_INCL_DIR)
MSGCOPTS = $(INCLUDE_PATH)

# we want to recompile everything if COPTS changes,
# so we store COPTS into $COPTS_FILE and have object
# files depend on it (except when "make depend" was called)
COPTS_FILE = $O/.last-copts
ifneq ($(MAKECMDGOALS),depend)
ifneq ("$(COPTS)","$(shell cat $(COPTS_FILE) 2>/dev/null || echo '')")
$(shell $(MKPATH) "$O" && echo "$(COPTS)" >$(COPTS_FILE))
endif
endif

#------------------------------------------------------------------------------
# User-supplied makefile fragment(s)
# >>>
# <<<
#------------------------------------------------------------------------------

# Main target
all: $O/$(TARGET)
	$(Q)$(LN) $O/$(TARGET) .

$O/$(TARGET): $(OBJS)  $(wildcard $(EXTRA_OBJS)) Makefile
	@$(MKPATH) $O
	@echo Creating executable: $@
	$(Q)$(CXX) $(LDFLAGS) -o $O/$(TARGET)  $(OBJS) $(EXTRA_OBJS) $(AS_NEEDED_OFF) $(WHOLE_ARCHIVE_ON) $(LIBS) $(WHOLE_ARCHIVE_OFF) $(OMNETPP_LIBS)

.PHONY: all clean cleanall depend msgheaders

.SUFFIXES: .cc

$O/%.o: %.cc $(COPTS_FILE)
	@$(MKPATH) $(dir $@)
	$(qecho) "$<"
	$(Q)$(CXX) -c $(CXXFLAGS) $(COPTS) -o $@ $<

%_m.cc %_m.h: %.msg
	$(qecho) MSGC: $<
	$(Q)$(MSGC) -s _m.cc $(MSGCOPTS) $?

msgheaders: $(MSGFILES:.msg=_m.h)

clean:
	$(qecho) Cleaning...
	$(Q)-rm -rf $O
	$(Q)-rm -f CCNSim CCNSim.exe libCCNSim.so libCCNSim.a libCCNSim.dll libCCNSim.dylib
	$(Q)-rm -f ./*_m.cc ./*_m.h
	$(Q)-rm -f include/*_m.cc include/*_m.h
	$(Q)-rm -f ini/*_m.cc ini/*_m.h
	$(Q)-rm -f modules/*_m.cc modules/*_m.h
	$(Q)-rm -f modules/clients/*_m.cc modules/clients/*_m.h
	$(Q)-rm -f modules/content/*_m.cc modules/content/*_m.h
	$(Q)-rm -f modules/node/*_m.cc modules/node/*_m.h
	$(Q)-rm -f modules/node/cache/*_m.cc modules/node/cache/*_m.h
	$(Q)-rm -f modules/node/strategy/*_m.cc modules/node/strategy/*_m.h
	$(Q)-rm -f modules/statistics/*_m.cc modules/statistics/*_m.h
	$(Q)-rm -f networks/*_m.cc networks/*_m.h
	$(Q)-rm -f packets/*_m.cc packets/*_m.h
	$(Q)-rm -f results/*_m.cc results/*_m.h
	$(Q)-rm -f results/abilene/*_m.cc results/abilene/*_m.h
	$(Q)-rm -f results/abilene/F-spr/*_m.cc results/abilene/F-spr/*_m.h
	$(Q)-rm -f results/abilene/F-spr/D-lce/*_m.cc results/abilene/F-spr/D-lce/*_m.h
	$(Q)-rm -f results/abilene/F-spr/D-lce/R-lru/*_m.cc results/abilene/F-spr/D-lce/R-lru/*_m.h
	$(Q)-rm -f results/abilene/F-spr/D-lce/R-lru/alpha-1/*_m.cc results/abilene/F-spr/D-lce/R-lru/alpha-1/*_m.h
	$(Q)-rm -f src/*_m.cc src/*_m.h
	$(Q)-rm -f src/clients/*_m.cc src/clients/*_m.h
	$(Q)-rm -f src/content/*_m.cc src/content/*_m.h
	$(Q)-rm -f src/node/*_m.cc src/node/*_m.h
	$(Q)-rm -f src/node/cache/*_m.cc src/node/cache/*_m.h
	$(Q)-rm -f src/node/strategy/*_m.cc src/node/strategy/*_m.h
	$(Q)-rm -f src/statistics/*_m.cc src/statistics/*_m.h

cleanall: clean
	$(Q)-rm -rf $(PROJECT_OUTPUT_DIR)

depend:
	$(qecho) Creating dependencies...
	$(Q)$(MAKEDEPEND) $(INCLUDE_PATH) -f Makefile -P\$$O/ -- $(MSG_CC_FILES)  ./*.cc include/*.cc ini/*.cc modules/*.cc modules/clients/*.cc modules/content/*.cc modules/node/*.cc modules/node/cache/*.cc modules/node/strategy/*.cc modules/statistics/*.cc networks/*.cc packets/*.cc results/*.cc results/abilene/*.cc results/abilene/F-spr/*.cc results/abilene/F-spr/D-lce/*.cc results/abilene/F-spr/D-lce/R-lru/*.cc results/abilene/F-spr/D-lce/R-lru/alpha-1/*.cc src/*.cc src/clients/*.cc src/content/*.cc src/node/*.cc src/node/cache/*.cc src/node/strategy/*.cc src/statistics/*.cc

# DO NOT DELETE THIS LINE -- make depend depends on it.
$O/packets/ccn_data_m.o: packets/ccn_data_m.cc \
	include/ccnsim.h \
	include/client.h \
	include/ctopology_s.h \
	packets/ccn_data_m.h
$O/packets/ccn_interest_m.o: packets/ccn_interest_m.cc \
	include/ccnsim.h \
	include/client.h \
	include/ctopology_s.h \
	packets/ccn_interest_m.h
$O/src/ctopology.o: src/ctopology.cc
$O/src/clients/client.o: src/clients/client.cc \
	include/ccn_data.h \
	include/ccn_interest.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/ctopology_s.h \
	include/statistics.h \
	include/zipf.h \
	packets/ccn_data_m.h \
	packets/ccn_interest_m.h
$O/src/content/content_distribution.o: src/content/content_distribution.cc \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/ctopology_s.h \
	include/zipf.h
$O/src/content/zipf.o: src/content/zipf.cc \
	include/zipf.h
$O/src/node/core_layer.o: src/node/core_layer.cc \
	include/base_cache.h \
	include/ccn_data.h \
	include/ccn_interest.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/core_layer.h \
	include/ctopology_s.h \
	include/strategy_layer.h \
	include/zipf.h \
	packets/ccn_data_m.h \
	packets/ccn_interest_m.h
$O/src/node/cache/base_cache.o: src/node/cache/base_cache.cc \
	include/always_policy.h \
	include/base_cache.h \
	include/betweenness_centrality.h \
	include/ccn_data.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/core_layer.h \
	include/ctopology_s.h \
	include/decision_policy.h \
	include/fix_policy.h \
	include/lcd_policy.h \
	include/never_policy.h \
	include/prob_cache.h \
	include/statistics.h \
	include/zipf.h \
	packets/ccn_data_m.h
$O/src/node/cache/fifo_cache.o: src/node/cache/fifo_cache.cc \
	include/base_cache.h \
	include/ccnsim.h \
	include/client.h \
	include/ctopology_s.h \
	include/fifo_cache.h
$O/src/node/cache/lru_cache.o: src/node/cache/lru_cache.cc \
	include/base_cache.h \
	include/ccnsim.h \
	include/client.h \
	include/ctopology_s.h \
	include/lru_cache.h
$O/src/node/cache/random_cache.o: src/node/cache/random_cache.cc \
	include/base_cache.h \
	include/ccnsim.h \
	include/client.h \
	include/ctopology_s.h \
	include/random_cache.h
$O/src/node/cache/two_cache.o: src/node/cache/two_cache.cc \
	include/base_cache.h \
	include/ccnsim.h \
	include/client.h \
	include/ctopology_s.h \
	include/two_cache.h
$O/src/node/strategy/nrr.o: src/node/strategy/nrr.cc \
	include/base_cache.h \
	include/ccn_interest.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/ctopology_s.h \
	include/nrr.h \
	include/strategy_layer.h \
	include/zipf.h \
	packets/ccn_interest_m.h
$O/src/node/strategy/nrr1.o: src/node/strategy/nrr1.cc \
	include/ccn_interest.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/ctopology_s.h \
	include/nrr1.h \
	include/strategy_layer.h \
	include/zipf.h \
	packets/ccn_interest_m.h
$O/src/node/strategy/parallel_repository.o: src/node/strategy/parallel_repository.cc \
	include/ccn_interest.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/ctopology_s.h \
	include/parallel_repository.h \
	include/strategy_layer.h \
	include/zipf.h \
	packets/ccn_interest_m.h
$O/src/node/strategy/random_repository.o: src/node/strategy/random_repository.cc \
	include/ccn_interest.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/ctopology_s.h \
	include/random_repository.h \
	include/strategy_layer.h \
	include/zipf.h \
	packets/ccn_interest_m.h
$O/src/node/strategy/spr.o: src/node/strategy/spr.cc \
	include/ccn_interest.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/ctopology_s.h \
	include/spr.h \
	include/strategy_layer.h \
	include/zipf.h \
	packets/ccn_interest_m.h
$O/src/node/strategy/strategy_layer.o: src/node/strategy/strategy_layer.cc \
	include/ccnsim.h \
	include/client.h \
	include/ctopology_s.h \
	include/strategy_layer.h
$O/src/statistics/statistics.o: src/statistics/statistics.cc \
	include/base_cache.h \
	include/ccnsim.h \
	include/client.h \
	include/content_distribution.h \
	include/core_layer.h \
	include/ctopology_s.h \
	include/lru_cache.h \
	include/statistics.h \
	include/zipf.h

