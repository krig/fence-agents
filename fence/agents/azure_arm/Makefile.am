MAINTAINERCLEANFILES= Makefile.in

TARGET= fence_azure

SRC= fence_azure

EXTRA_DIST= $(SRC)

sbin_SCRIPTS= $(TARGET)

man_MANS= fence_azure.8

FENCE_TEST_ARGS         = -l test -p test -a test -n 1

include $(top_srcdir)/make/fencebuild.mk
include $(top_srcdir)/make/fenceman.mk

