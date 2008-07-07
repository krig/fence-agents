#include "fd.h"

#define DEFAULT_MODE		LOG_MODE_OUTPUT_SYSLOG_THREADED
#define DEFAULT_FACILITY	SYSLOGFACILITY /* cluster config setting */
#define DEFAULT_PRIORITY	SYSLOGLEVEL /* cluster config setting */
#define DEFAULT_FILE		LOGDIR "/fenced.log"

#define LEVEL_PATH "/cluster/logging/logger_subsys[@subsys=\"FENCED\"]/@syslog_level"
#define DEBUG_PATH "/cluster/logging/logger_subsys[@subsys=\"FENCED\"]/@debug"

/* Read cluster.conf settings and convert them into logsys values.
   If no cluster.conf setting exists, the default that was used in
   logsys_init() is used.

   mode from
   "/cluster/logging/@to_stderr"
   "/cluster/logging/@to_syslog"
   "/cluster/logging/@to_file"

   facility from
   "/cluster/logging/@syslog_facility"

   priority from
   "/cluster/logging/logger_subsys[@subsys=\"prog_name\"]/@syslog_level"

   file from
   "/cluster/logging/@logfile"

   debug from
   "/cluster/logging/@debug"
   "/cluster/logging/logger_subsys[@subsys=\"prog_name\"]/@debug"
*/

static int read_ccs_logging(int *mode, int *facility, int *priority, char *file,
			    int *debug)
{
	char name[PATH_MAX];
	int val, y, n;
	int m = 0, f = 0, p = 0;

	/*
	 * mode
	 */

	m = DEFAULT_MODE;

	read_ccs_yesno("/cluster/logging/@to_stderr", &y, &n);
	if (y)
		m |= LOG_MODE_OUTPUT_STDERR;
	if (n)
		m &= ~LOG_MODE_OUTPUT_STDERR;

	read_ccs_yesno("/cluster/logging/@to_syslog", &y, &n);
	if (y)
		m |= LOG_MODE_OUTPUT_SYSLOG_THREADED;
	if (n)
		m &= ~LOG_MODE_OUTPUT_SYSLOG_THREADED;

	read_ccs_yesno("/cluster/logging/@to_file", &y, &n);
	if (y)
		m |= LOG_MODE_OUTPUT_FILE;
	if (n)
		m &= ~LOG_MODE_OUTPUT_FILE;

	*mode = m;

	/*
	 * facility
	 */

	f = DEFAULT_FACILITY;

	memset(name, 0, sizeof(name));
	read_ccs_name("/cluster/logging/@syslog_facility", name);

	if (name[0]) {
		val = logsys_facility_id_get(name);
		if (val >= 0)
			f = val;
	}

	*facility = f;

	/*
	 * priority
	 */

	p = DEFAULT_PRIORITY;

	memset(name, 0, sizeof(name));
	read_ccs_name(LEVEL_PATH, name);

	if (name[0]) {
		val = logsys_priority_id_get(name);
		if (val >= 0)
			p = val;
	}

	*priority = p;

	/*
	 * file
	 */

	strcpy(file, DEFAULT_FILE);

	memset(name, 0, sizeof(name));
	read_ccs_name("/cluster/logging/@logfile", name);

	if (name[0])
		strcpy(file, name);

	/*
	 * debug
	 */

	memset(name, 0, sizeof(name));
	read_ccs_name("/cluster/logging/@debug", name);

	if (!strcmp(name, "on"))
		*debug = 1;

	memset(name, 0, sizeof(name));
	read_ccs_name(DEBUG_PATH, name);

	if (!strcmp(name, "on"))
		*debug = 1;
	else if (!strcmp(name, "off"))
		*debug = 0;

	return 0;
}

/* initial settings until we can read cluster.conf logging settings from ccs */

void init_logging(void)
{
	logsys_init("fenced", DEFAULT_MODE, DEFAULT_FACILITY, DEFAULT_PRIORITY,
		    DEFAULT_FILE);
}

/* this function is also called when we get a cman config-update event */

void setup_logging(int *prog_debug)
{
	int mode, facility, priority;
	char file[PATH_MAX];

	/* The debug setting is special, it's used by the program
	   and not used to configure logsys. */

	read_ccs_logging(&mode, &facility, &priority, file, prog_debug);
	logsys_conf("fenced", mode, facility, priority, file);
}

void close_logging(void)
{
	logsys_exit();
}
