from logging import info, Filter
from os import getenv, sep as os_sep
from os.path import abspath, relpath
from sys import path as sys_path


class PackagePathFilter(Filter):
    def filter(self, record):
        pathname = record.pathname
        record.relativepath = None
        abs_sys_paths = map(abspath, sys_path)
        for path in sorted(abs_sys_paths, key=len, reverse=True):
            if not path.endswith(os_sep):
                path += os_sep
            if pathname.startswith(path):
                record.relativepath = relpath(pathname, path)
                break
        return True


LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "package_path_filter": {
            "()": PackagePathFilter,
        },
    },
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s [%(relativepath)s:%(lineno)d] %(message)s",
            "use_colors": True,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
        },
        'verbose': {
            'format': '[%(levelname)s] [T%(thread)d] [%(relativepath)s:%(lineno)d] [%(funcName)s] %(message)s',  # noqa: E501
            "use_colors": None,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        'sys-logger7': {
            'class': 'logging.handlers.SysLogHandler',
            "address": ["127.0.0.1", 514],
            'facility': "local7",
            'formatter': 'verbose',
            "filters": ["package_path_filter"],
        },
    },
    "loggers": {
        "root": {
            "handlers": ["sys-logger7", "default"],
            "level": "DEBUG",
            "propagate": False,
        },
        # "uvicorn": {"handlers": ["default", "sys-logger7"], "level": "INFO"},
        # "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {
            "handlers": ["access", "sys-logger7"],
            "level": "INFO",
            "propagate": False
        },
    },
}


if __name__ == "__main__":
    import uvicorn
    host = getenv('HOST', '0.0.0.0')
    port = getenv('PORT', '8005')
    info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "api.main:app",
        host=host,
        port=int(port),
        log_level="debug",
        reload=True,
        log_config=LOGGING_CONFIG,
    )
