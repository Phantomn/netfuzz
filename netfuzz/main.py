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

def handle_sigint(signum, frame):
    print("CTRL+C Pressed, exiting...")
    sys.exit(0)

def setup_process_monitor(args, crash_filename="crashes"):
    """
    Setup the process monitor based on the provided arguments.
    """
    if len(args.target_cmdline) > 0 and args.procmon_host is None:
        procmon = ProcessMonitorLocal(
            crash_filename=crash_filename,
            proc_name=None,
            pid_to_ignore=None,
            debugger_class=DebuggerThreadSimple,
            level=1)
    else:
        procmon = None

    procmon_options = {}
    if args.procmon_start:
        procmon_options['start_commands'] = [args.procmon_start]
    if args.target_cmdline:
        procmon_options['start_commands'] = [args.target_cmdline]
    if args.procmon_capture:
        procmon_options['capture_output'] = True

    if procmon:
        procmon.set_options(**procmon_options)

    if args.procmon_host:
        procmon = ProcessMonitor(
            host=args.procmon_host,
            port=args.procmon_port)
        procmon.set_options(**procmon_options)

    return procmon

def setup_fuzz_loggers(args):
    """
    Setup the fuzz loggers based on the provided arguments.
    """
    fuzz_loggers = []
    if args.text_dump:
        fuzz_loggers.append(FuzzLoggerText())
    if args.tui:
        fuzz_loggers.append(FuzzLoggerCurses())
    if args.csv_out:
        f = open(args.csv_out, 'w')
        fuzz_loggers.append(FuzzLoggerCsv(file_handle=f))

    return fuzz_loggers

def configure_session_indices(session, args):
    """
    Configure the fuzzing session start and end indices based on arguments.
    """
    start = None
    end = None
    fuzz_only_one_case = None
    if args.test_case_index is None:
        start = 1
    elif "-" in args.test_case_index:
        start, end = args.test_case_index.split("-")
        start = int(start) if start else 1
        end = int(end) if end else None
    else:
        fuzz_only_one_case = int(args.test_case_index)

    session.index_start = start
    session.index_end = end
    return fuzz_only_one_case

def run_fuzzing(session, args, fuzz_only_one_case):
    """
    Run the fuzzing session based on the provided arguments.
    """
    if args.feature_check:
        session.feature_check()
    elif fuzz_only_one_case is not None:
        session.fuzz_single_case(mutant_index=fuzz_only_one_case)
    elif args.test_case_name is not None:
        session.fuzz_by_name(args.test_case_name)
    else:
        session.fuzz()

def main():
    signal.signal(signal.SIGINT, handle_sigint)  # Register signal handler for CTRL+C

    args = parse_args()

    procmon = setup_process_monitor(args)
    fuzz_loggers = setup_fuzz_loggers(args)

    connection = TCPSocketConnection(args.target_host, args.target_port)

    session = Session(
        target=Target(connection=connection, monitors=[procmon] if procmon else []),
        fuzz_loggers=fuzz_loggers,
        sleep_time=args.sleep_between_cases
    )

    # Initialize FTP strategy with username and password
    ftp = FTP(username=args.username, password=args.password)
    ftp.setup_session(session)

    fuzz_only_one_case = configure_session_indices(session, args)
    
    try:
        run_fuzzing(session, args, fuzz_only_one_case)
    finally:
        # Ensure resources are properly released
        for logger in fuzz_loggers:
            if hasattr(logger, 'close'):
                logger.close()
        if procmon:
            procmon.stop_target()

if __name__ == "__main__":
    main()
