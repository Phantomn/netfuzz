import argparse
import sys
import signal
from protocols.ftp import FTP
from boofuzz import Session, Target, TCPSocketConnection
from boofuzz.constants import DEFAULT_PROCMON_PORT
from boofuzz.monitors import ProcessMonitor
from boofuzz.utils.process_monitor_local import ProcessMonitorLocal
from boofuzz.utils.debugger_thread_simple import DebuggerThreadSimple
from boofuzz import FuzzLoggerText, FuzzLoggerCsv, FuzzLoggerCurses

def parse_args():
    parser = argparse.ArgumentParser(description="Network Protocol Fuzzer")
    parser.add_argument('--target-host', required=True, help='Host or IP address of target')
    parser.add_argument('--target-port', type=int, default=21, help='Network port of target')
    parser.add_argument('--username', required=True, help='FTP username')
    parser.add_argument('--password', required=True, help='FTP password')
    parser.add_argument('--test-case-index', help='Test case index', type=str)
    parser.add_argument('--test-case-name', help='Name of node or specific test case')
    parser.add_argument('--csv-out', help='Output to CSV file')
    parser.add_argument('--sleep-between-cases', type=float, default=0, help='Wait time between test cases')
    parser.add_argument('--procmon-host', help='Process monitor host or IP')
    parser.add_argument('--procmon-port', type=int, default=DEFAULT_PROCMON_PORT, help='Process monitor port')
    parser.add_argument('--procmon-start', help='Process monitor start command')
    parser.add_argument('--procmon-capture', action='store_true', help='Capture stdout/stderr from target process upon failure')
    parser.add_argument('--tui', action='store_true', help='Enable TUI')
    parser.add_argument('--text-dump', action='store_true', help='Enable full text dump of logs')
    parser.add_argument('--feature-check', action='store_true', help='Run a feature check instead of a fuzz test')
    parser.add_argument('target_cmdline', nargs=argparse.REMAINDER, help='Target command line for process monitor')
    return parser.parse_args()

def handle_sigint(signal, frame):
    print("CTRL+C Pressed, exiting...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_sigint)
    
    args = parse_args()
    
    local_procmon = None
    
    if len(args.target_cmdline) > 0 and args.procmon_host is None:
        local_procmon = ProcessMonitorLocal(
            crash_filename="crashes",
            proc_name=None,
            pid_to_ignore=None,
            debugger_class=DebuggerThreadSimple,
            level=1)

    fuzz_loggers = []
    if args.text_dump:
        fuzz_loggers.append(FuzzLoggerText())
    if args.tui:
        fuzz_loggers.append(FuzzLoggerCurses())
    if args.csv_out:
        with open(args.csv_out, 'w') as f:
            fuzz_loggers.append(FuzzLoggerCsv(file_handle=f))

    procmon_options = {}
    if args.procmon_start:
        procmon_options['start_commands'] = [args.procmon_start]
    if args.target_cmdline:
        procmon_options['start_commands'] = [args.target_cmdline]
    if args.procmon_capture:
        procmon_options['capture_output'] = True

    if local_procmon or args.procmon_host:
        if args.procmon_host:
            procmon = ProcessMonitor(
                host=args.procmon_host,
                port=args.procmon_port)
        else:
            procmon = local_procmon
        procmon.set_options(**procmon_options)
        monitors = [procmon]
    else:
        monitors = []

    start = None
    end = None
    fuzz_only_one_case = None
    if args.test_case_index is None:
        start = 1
    elif "-" in args.test_case_index:
        start, end = args.test_case_index.split("-")
        if not start:
            start = 1
        else:
            start = int(start)
        if not end:
            end = None
        else:
            end = int(end)
    else:
        fuzz_only_one_case = int(args.test_case_index)

    connection = TCPSocketConnection(args.target_host, args.target_port)

    session = Session(target=Target(connection=connection, monitors=monitors),
                      fuzz_loggers=fuzz_loggers,
                      sleep_time=args.sleep_between_cases,
                      index_start=start,
                      index_end=end)

    ftp = FTP(username=args.username, password=args.password)
    ftp.setup_session(session)

    try:
        if args.feature_check:
            session.feature_check()
        elif fuzz_only_one_case is not None:
            session.fuzz_single_case(mutant_index=fuzz_only_one_case)
        elif args.test_case_name is not None:
            session.fuzz_by_name(args.test_case_name)
        else:
            session.fuzz()
    finally:
        for logger in fuzz_loggers:
            if hasattr(logger, 'close'):
                logger.close()
        if local_procmon or args.procmon_host:
            procmon.stop_target()

if __name__ == "__main__":
    main()
