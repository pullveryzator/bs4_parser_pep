from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_PAGE = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FOR_FILE_FORMAT = '%Y-%m-%d_%H-%M-%S'
MAX_LOG_LENGTH = 10 ** 6
BACKUP_COUNT = 5
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DATETIME_FOR_LOG_FORMAT = '%d.%m.%Y %H:%M:%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred', ),
    'F': ('Final', ),
    'P': ('Provisional', ),
    'R': ('Rejected', ),
    'S': ('Superseded', ),
    'W': ('Withdrawn', ),
    '': ('Draft', 'Active'),
}
